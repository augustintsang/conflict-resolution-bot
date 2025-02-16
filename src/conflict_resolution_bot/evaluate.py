# evaluate.py

import os
import json
from typing import List
from pydantic import BaseModel
from google import genai
import weave

from app import app  # shared FastAPI instance

#
# Data Models
#
class EvaluateInput(BaseModel):
    conversation: str

class EvaluateOutput(BaseModel):
    topic: str
    context: str
    Information_request: str

#
# Endpoint & Logic
#
@app.post("/evaluate_conversation", response_model=List[EvaluateOutput])
@weave.op()
def evaluate_conversation_endpoint(input_data: EvaluateInput):
    """
    This endpoint returns a JSON array of:
      [ { "topic": "...", "context": "...", "Information_request": "..." }, ... ]
    """
    return evaluate_conversation_logic(input_data)

def evaluate_conversation_logic(input_data: EvaluateInput) -> List[dict]:
    """
    Plain Python function for evaluating the conversation via Gemini.
    """
    system_prompt = """
    You are reviewing a conversation among multiple participants.

    Your goal is to produce a JSON array containing each piece of information
    the team needs to look up or clarify to resolve the conversation.

    The output:
    - MUST be valid JSON conforming to the schema below:
      [
        {
          "topic": "some string",
          "context": "some string",
          "Information_request": "some string"
        }
      ]
    - MUST NOT include additional commentary or formatting.
    """

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    response = client.models.generate_content(
        model="models/gemini-2.0-flash",
        contents=input_data.conversation,
        config={
            "response_mime_type": "application/json",
            "system_instruction": system_prompt,
            "response_schema": list[EvaluateOutput],  # built-in
            "temperature": 0
        }
    )

    return json.loads(response.text)
