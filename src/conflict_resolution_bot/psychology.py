# psychology.py

import os
import json
import openai
from typing import List
from pydantic import BaseModel
import weave

# Import the shared FastAPI app (no circular imports)
from app import app

#
# Data Models
#
class PsychologyInput(BaseModel):
    conversation: str

class PsychologyOutput(BaseModel):
    Person: str
    Tone: str
    Emotional_state: str
    Core_objective: str

#
# Configure your Sambanova/OpenAI API client
#
client = openai.OpenAI(
    api_key=os.environ.get("SAMBANOVA_API_KEY"),
    base_url="https://preview.snova.ai/v1",
)

#
# Endpoint & Logic
#
@app.post("/psychology", response_model=List[PsychologyOutput])
@weave.op()
def psychology_endpoint(input_data: PsychologyInput):
    """
    This endpoint returns a JSON array conforming to the schema:
    [
      {
        "Person": "some string",
        "Tone": "some string",
        "Emotional_state": "some string",
        "Core_objective": "some string"
      }
    ]
    describing the tone and emotional state of each participant.
    """
    return psychology_logic(input_data)


def psychology_logic(input_data: PsychologyInput) -> List[dict]:
    """
    Plain Python function that does the real work.
    Returns a list of dicts with the keys:
      - Person
      - Tone
      - Emotional_state
      - Core_objective
    """
    system_prompt = """
You are reviewing a conversation among multiple participants.

Your goal is to produce a JSON array containing an evaluation of the tone and emotional state of each participant in the conversation based on their statements and responses. 

The output:
- MUST be valid JSON conforming to the schema below:
  [
    {
      "Person": "some string",
      "Tone": "some string",
      "Emotional_state": "some string",
      "Core_objective": "some string"
    }
  ]
- MUST NOT include additional commentary or formatting.
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": input_data.conversation}
    ]

    response = client.chat.completions.create(
        model="DeepSeek-R1",     # Or whichever model you prefer
        messages=messages,
        temperature=0.1,
        top_p=0.0
    )

    # The model response will be in response.choices[0].message.content
    raw_content = response.choices[0].message.content

    # Attempt to parse the content as JSON
    try:
        data = json.loads(raw_content)
    except json.JSONDecodeError as e:
        raise ValueError("Failed to parse model output as valid JSON array.") from e

    return data
