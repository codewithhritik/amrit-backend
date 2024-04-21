import json
import asyncio
from fastapi import FastAPI
from uagents import Model
from uagents.query import query
from pydantic import BaseModel
from uagents.context import send_sync_message

AGENT_ADDRESS = "agent1qfvptjx47glk0ud04x3asxc2s2jzu5gu5wagtpp7ck4l9l6vmzs4vtzfw6t"

class ImageRequest(BaseModel):
    image_base64: str
    task: str

async def agent_query(req):
    response = await query(destination=AGENT_ADDRESS, message=req)
    data = json.loads(response.decode_payload())
    print(data)
    # clean_response = data["text"]
    # clean_response = clean_response.replace("```json", "").replace("```", "").strip()
    # # Convert the cleaned string to a JSON object
    # response_json = json.loads(clean_response)
    # return response_json
    return data["text"]

app = FastAPI()

@app.get("/")
def read_root():
    return "Hello from Amrit Server - Image to text Agent"

@app.post("/image-to-text")
async def make_gemini_call(req: ImageRequest):
    try:
        print("Req is -", req)
        print(req.task)
        res = await agent_query(req)
        return res
    except Exception as ex:
        print(ex)
        return "unsuccessful agent call - gemini"