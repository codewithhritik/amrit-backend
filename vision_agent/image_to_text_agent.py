# Importing necessary libraries
from uagents import Agent, Context
from uagents.setup import fund_agent_if_low
from uagents import Model
import google.generativeai as genai
from pydantic import BaseModel
import base64
from PIL import Image
from io import BytesIO
import json
from uagents.context import send_sync_message

# Defining a model for messages
class Message(Model):
    message: str

class Response(Model):
    text: str

class ImageRequest(BaseModel):
    image_base64: str
    task: str

class ComparisonRequest(BaseModel):
    description: str
    task: str

RECIPIENT_ADDRESS="agent1qwnyystfdj8ldgts5vxqxhvrvt09d83kla077kkhkypu7p4ehkdhxlhhg46"

# Defining the user agent
Gemini_vision_agent = Agent(
    name="Gemini Image to Text Agent",
    port=8002,
    seed="Gemini Agent secret phrase lol - it converts image to text",
    endpoint=["http://localhost:8002/submit"],
)

print(Gemini_vision_agent.address)
 
# Funding the user agent if its wallet balance is low
fund_agent_if_low(Gemini_vision_agent.wallet.address())

# Configuring the API key for Google's generative AI service
genai.configure(api_key='AIzaSyANvgl8Qc8lW3bPOxtcFzj7yFgkjbPBxZE') #replace your gemini API key here

# Initializing the generative model with a specific model name
model = genai.GenerativeModel('models/gemini-pro-vision')
    
# Starting a new chat session
chat = model.start_chat(history=[])

print("Chat session has started. Type 'quit' to exit.")

# Function to handle incoming messages
async def handle_message(image_base64, task):
    while True:
      # Get user input
      # Decode the image from base64 string
      image_data = base64.b64decode(image_base64.split(",")[1])
      image = Image.open(BytesIO(image_data))

      # Generate description
      prompt = """Look at this image, and describe what is happening in the image, make sure you capture every detail of it and return a paragraph containing the complete description"""

      # Inside handle_message function
      print("Generated prompt:", prompt)
          
      # Send the message to the chat session and receive a streamed response
      response = model.generate_content([prompt, image])

      print("Response Object", response.text)
      
      # Initialize an empty string to accumulate the response text
      full_response_text = ""
      
      # Accumulate the chunks of text
      for chunk in response:
          full_response_text += chunk.text
          
      # Print the accumulated response as a single paragraph
      message = full_response_text
      return message
        
# Event handler for agent startup
@Gemini_vision_agent.on_event('startup')
async def address(ctx: Context):
    # Logging the agent's address
    ctx.logger.info(Gemini_vision_agent.address)
    
@Gemini_vision_agent.on_query(model=ImageRequest, replies={Response})
async def query_handler(ctx: Context, sender: str, msg: ImageRequest):
    ctx.logger.info("Query received")
    try:
        # Handling the incoming message
        message = await handle_message(msg.image_base64, msg.task)
        
        # Logging the response
        ctx.logger.info(message)

        # await ctx.send(sender, Response(text=message))
        response = await send_sync_message(
        RECIPIENT_ADDRESS, ComparisonRequest(description=message, task=msg.task), response_type=ComparisonRequest
        )
        # resp = await ctx.send(RECIPIENT_ADDRESS, ComparisonRequest(description=message, task=msg.task))
        print(response)

        await ctx.send(sender, Response(text=response))
    except Exception as e:
        ctx.logger.error(f"Error processing message: {str(e)}")
        await ctx.send(sender, Response(text="fail from gemini agent"))

@Gemini_vision_agent.on_message(model=Response)
async def message_handler(ctx: Context, sender: str, msg: Response):
    ctx.logger.info(f"Received message from {sender}: {msg.text}")

if __name__ == "__main__":
    Gemini_vision_agent.run()