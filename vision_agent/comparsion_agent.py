# Importing necessary libraries
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
import google.generativeai as genai
from pydantic import BaseModel

class ComparisonRequest(BaseModel):
    description: str
    task: str

class Response(Model):
    text: str

# Defining the user agent
Gemini_comparsion_agent = Agent(
    name="Gemini Text to Text Comparison Agent",
    port=8003,
    seed="Gemini Agent secret phrase lol - it checks similarity of texts",
    endpoint=["http://localhost:8003/submit"],
)

print(Gemini_comparsion_agent.address)

fund_agent_if_low(Gemini_comparsion_agent.wallet.address())

# Configuring the API key for Google's generative AI service
genai.configure(api_key='AIzaSyANvgl8Qc8lW3bPOxtcFzj7yFgkjbPBxZE')

model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")

# Starting a new chat session
chat = model.start_chat(history=[])

# Function to handle incoming messages
async def handle_message(task, description):
    while True:

      prompt = f"""I will give you a detailed explanation of an image , and a task that the user had to perform. you have to compare the image description and the task and then you have to return how much you are confident that the task was completed. the format of the output should be mandatorily in pure json with 'result' being the key and either 'true' if you think task is completed or 'false' if you think task is not completed. here is the image description {description} and here is the task user was asked to do {task}"""

      # Inside handle_message function
      print("Generated prompt:", prompt)

          
      # Send the message to the chat session and receive a streamed response
      response = model.generate_content([prompt])

      print("Response Object", response)
      
      # Initialize an empty string to accumulate the response text
      full_response_text = ""
      
      # Accumulate the chunks of text
      for chunk in response:
          full_response_text += chunk.text
          
      # Print the accumulated response as a single paragraph
      message = full_response_text
      return message

@Gemini_comparsion_agent.on_message(model=ComparisonRequest, replies={Response})
async def message_handler(ctx: Context, sender: str, msg: ComparisonRequest):
    ctx.logger.info(f"Received message from {sender}: {msg.task}")
    print("Task is - ", msg.task)
    print("Description is - ", msg.description)

    try:
        # Handling the incoming message
        message = await handle_message(msg.task, msg.description)
        
        # Logging the response
        ctx.logger.info(message)
        await ctx.send(sender, Response(text=message))
    except Exception as e:
        ctx.logger.error(f"Error processing message: {str(e)}")
        await ctx.send(sender, Response(text="fail from gemini agent"))

if __name__ == "__main__":
    Gemini_comparsion_agent.run()