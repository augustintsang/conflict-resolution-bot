from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import os
from google import genai
import uvicorn
import json

# 1) Define a Pydantic model matching your desired JSON schema for the output.
class InfoItem(BaseModel):
    Objective: str

# 2) Define a Pydantic model for the input (the conversation).
class ConversationInput(BaseModel):
    conversation: str

# Create the FastAPI app
app = FastAPI()

@app.post("/generate_objective", response_model=List[InfoItem])
def generate_objective(conversation_input: ConversationInput):
    """
    This endpoint generates a JSON array of objects matching the schema:
    [
      {
        "Objective": "some string"
      },
      ...
    ]
    It takes a conversation string as input, then uses Gemini to parse out the conversation's objective(s).
    """

    # The system prompt telling the model exactly what to do.
    system_prompt = """
    You are reviewing a conversation among multiple participants.

    Your goal is to produce a JSON array containing the objective of the conversation.

    The output:
    - MUST be valid JSON conforming to the schema below:
      [
        {
          "Objective": "some string"
        }
      ]
    - MUST NOT include additional commentary or formatting.

    For example, if they discussed “Crew AI,” a valid object might be:
    {
      "Objective": "Create a cookie recipe"
    }

    Return ONLY the JSON array, nothing else.
    """

    # Pull conversation from the input.
    conversation = conversation_input.conversation

    # Initialize the genai client. 
    # Make sure your environment has GEMINI_API_KEY set, or replace with a real key.
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    # Generate the content with forced JSON extraction & validation.
    response = client.models.generate_content(
        model="models/gemini-2.0-flash",
        contents=conversation,         # The conversation or "user" message
        config={
            "response_mime_type": "application/json",
            "system_instruction": system_prompt,
            "response_schema": list[InfoItem],
            "temperature": 0
        }
    )

    # Return the raw JSON parsed into Python objects so FastAPI can enforce the schema.
    return json.loads(response.text)

# Optional: If you want to run directly via `python my_file.py`
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
