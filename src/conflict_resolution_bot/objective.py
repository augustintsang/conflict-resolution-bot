# objective.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import os
import json
import uvicorn
from google import genai

#
# OBJECTIVE MODELS
#
class ObjectiveInput(BaseModel):
    """Pydantic model for the request body containing the conversation."""
    conversation: str

class ObjectiveOutput(BaseModel):
    """Pydantic model for the output: a list of objectives."""
    Objective: str

# Create a single FastAPI 'app' instance
app = FastAPI()

@app.post("/generate_objective", response_model=List[ObjectiveOutput])
def generate_objective(input_data: ObjectiveInput):
    """
    This endpoint generates a JSON array matching the schema:
      [
        {
          "Objective": "some string"
        }
      ]
    It takes a conversation string as input, then uses Gemini to parse out the conversation's objective(s).
    """

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

    conversation = input_data.conversation

    # Initialize the genai client
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    # Generate the content with forced JSON extraction & validation.
    response = client.models.generate_content(
        model="models/gemini-2.0-flash",
        contents=conversation,
        config={
            "response_mime_type": "application/json",
            "system_instruction": system_prompt,
            # IMPORTANT: Use the built-in `list` syntax:
            "response_schema": list[ObjectiveOutput],
            "temperature": 0
        }
    )

    # Convert the raw JSON string to a Python list/dict
    return json.loads(response.text)

#
# IMPORTANT: Import `evaluate` here so that /evaluate_conversation is also attached
# to the same 'app' instance. This must happen AFTER app = FastAPI() is defined.
#
import evaluate  # noqa: E402

# If running this file directly: `python objective.py`
if __name__ == "__main__":
    uvicorn.run("objective:app", host="0.0.0.0", port=8000, reload=False)
