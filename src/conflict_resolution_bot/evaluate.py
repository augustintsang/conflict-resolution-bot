# evaluate.py

import os
import json
from typing import List
from pydantic import BaseModel
from google import genai

# Import the 'app' object from objective.py
from objective import app

#
# EVALUATION MODELS
#
class EvaluateInput(BaseModel):
    """Pydantic model for the request body containing the conversation."""
    conversation: str

class EvaluateOutput(BaseModel):
    """Pydantic model for each info request in the conversation."""
    topic: str
    context: str
    Information_request: str

@app.post("/evaluate_conversation", response_model=List[EvaluateOutput])
def evaluate_conversation(input_data: EvaluateInput):
    """
    This endpoint produces a JSON array matching the schema:
      [
        {
          "topic": "some string",
          "context": "some string",
          "Information_request": "some string"
        }
      ]
    It takes a conversation string as input, then uses Gemini to parse out information requests.
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
        },
        ...
      ]
    - MUST NOT include additional commentary or formatting.

    For example, if they discussed “Crew AI,” a valid object might be:
    {
      "topic": "Cookies",
      "context": "We're exploring cookie recipes",
      "Information_request": "Which type of flour is best for baking cookies?"
    }

    Return ONLY the JSON array, nothing else.
    """

    conversation = input_data.conversation

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    # Generate the content with forced JSON extraction & validation.
    response = client.models.generate_content(
        model="models/gemini-2.0-flash",
        contents=conversation,
        config={
            "response_mime_type": "application/json",
            "system_instruction": system_prompt,
            # IMPORTANT: Use the built-in `list` syntax:
            "response_schema": list[EvaluateOutput],
            "temperature": 0
        }
    )

    return json.loads(response.text)
