# Importing necessary libraries
from uagents import Agent, Context
from uagents.setup import fund_agent_if_low
from uagents import Model
import google.generativeai as genai

# Defining a model for messages
class Message(Model):
    message: str

class Response(Model):
    text: str

# Defining the user agent
Gemini_agent = Agent(
    name="Gemini Agent",
    port=8001,
    seed="Gemini Agent secret phrase",
    endpoint=["http://localhost:8001/submit"],
)

print(Gemini_agent.address)
 
# Funding the user agent if its wallet balance is low
fund_agent_if_low(Gemini_agent.wallet.address())

# Configuring the API key for Google's generative AI service
genai.configure(api_key='AIzaSyANvgl8Qc8lW3bPOxtcFzj7yFgkjbPBxZE') #replace your gemini API key here

# Initializing the generative model with a specific model name
model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")
    
# Starting a new chat session
chat = model.start_chat(history=[])

print("Chat session has started. Type 'quit' to exit.")

# Function to handle incoming messages
async def handle_message(message):
    while True:
      # Get user input
      user_message = message
      
      # Check if the user wants to quit the conversation
    #   if user_message.lower() == 'quit':
    #       return "Exiting chat session."

      prompt = f"""you are an agent that will give me 10 tasks based on the addiction I will give you, make sure the tasks can be crosschecked by clicking a photo because i would be checking if the user has completed the task or not. also with every task give a suggestion what the photo could be. for example if you have given the task as drink water, the expected image would be "a selfie of you drinking water" and a description why this task benefit the user. Also give me all of these in json format where there are just tasks, expected photo, and description it requires. Now i will tell you what addiction the user is facing: {user_message}"""

      # Inside handle_message function
      print("Generated prompt:", prompt)

          
      # Send the message to the chat session and receive a streamed response
      response = model.generate_content([prompt])

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
@Gemini_agent.on_event('startup')
async def address(ctx: Context):
    # Logging the agent's address
    ctx.logger.info(Gemini_agent.address)

# Handler for query given by user
# @Gemini_agent.on_message(model=Message)
# async def handle_query_response(ctx: Context, sender: str, msg: Message):
#     # Handling the incoming message
#     message = await handle_message(msg.message)
    
#     # Logging the response
#     ctx.logger.info(message)
    
#     # Sending the response back to the sender
#     await ctx.send(sender, Message(message=message))
    
@Gemini_agent.on_query(model=Message, replies={Response})
async def query_handler(ctx: Context, sender: str, msg: Message):
    ctx.logger.info("Query received")
    try:
        # Handling the incoming message
        message = await handle_message(msg.message)
        
        # Logging the response
        ctx.logger.info(message)
        await ctx.send(sender, Response(text=message))
    except Exception as e:
        ctx.logger.error(f"Error processing message: {str(e)}")
        await ctx.send(sender, Response(text="fail from gemini agent"))

if __name__ == "__main__":
    Gemini_agent.run()