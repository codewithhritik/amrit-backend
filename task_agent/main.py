import json

from fastapi import FastAPI
from uagents import Model
from uagents.query import query

AGENT_ADDRESS = "agent1qwg20ukwk97t989h6kc8a3sev0lvaltxakmvvn3sqz9jdjw4wsuxqa45e8l"

class Message(Model):
    message: str

async def agent_query(req):
    response = await query(destination=AGENT_ADDRESS, message=req)
    data = json.loads(response.decode_payload())
    print(data)
    clean_response = data["text"]
    clean_response = clean_response.replace("```json", "").replace("```", "").strip()
    # Convert the cleaned string to a JSON object
    response_json = json.loads(clean_response)
    return response_json

app = FastAPI()

@app.get("/")
def read_root():
    return "Hello from Amrit Server - Task Agent"

@app.post("/send-prompt-to-gemini")
async def make_gemini_call(req: Message):
    try:
        print("Req is -", req)
        print(req.message)
        res = await agent_query(req)
        return res
    except Exception as ex:
        print(ex)
        return "unsuccessful agent call - gemini"