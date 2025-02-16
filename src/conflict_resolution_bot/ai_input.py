# AI_input.py

import json
from typing import List
from pydantic import BaseModel
from litellm import completion
import weave
import os

from app import app  # Import the shared FastAPI app (no circular import)

#
# Data Models
#
class AIInput(BaseModel):
    conversation: str
    ai_thoughts: str

class AIOutput(BaseModel):
    AI_Input: str

#
# Endpoint & Logic
#
@app.post("/generate_ai_input", response_model=List[AIOutput])
@weave.op()
def generate_ai_input_endpoint(input_data: AIInput):
    """
    This endpoint returns a JSON array:
      [ { "AI_Input": "some string" } ]
    derived from the conversation string and AI thoughts.
    """
    return generate_ai_input_logic(input_data)

def generate_ai_input_logic(input_data: AIInput) -> List[dict]:
    """
    Plain Python function that does the real work.
    Return e.g. [ { "AI_Input": "some string" }, ... ]
    based on both conversation & AI thoughts.
    """
    system_prompt = """
    You are reviewing a conversation among multiple participants, along with the AI's internal thoughts.

    Your goal is to produce a JSON array containing a single key "AI_Input" that concisely captures the essential instruction or conclusion derived from BOTH:
    1) The conversation
    2) The AI's thoughts

    The output:
    - MUST be valid JSON conforming to the schema below:
    - Must be natural, provide feedback that is helpful to the conversation and relatively concise.
      [
        {
          "AI_Input": "some string"
        }
      ]
    - MUST NOT include additional commentary or formatting.
    """

    # Combine the conversation + AI thoughts in the user message
    user_content = (
        f"Conversation:\n{input_data.conversation}\n\n"
        f"AI thoughts:\n{input_data.ai_thoughts}"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]

    # Example usage of litellm completion
    response = completion(
        model="sambanova/Meta-Llama-3.1-8B-Instruct",
        messages=messages,
        response_format={"type": "json_object"}  # parse the output as JSON
    )

    try:
        content = response["choices"][0]["message"]["content"]
        ai_input_data = json.loads(content)
    except Exception as e:
        raise ValueError("Failed to parse model output as valid JSON array.") from e

    # `ai_input_data` should be a list of { "AI_Input": ... }
    return ai_input_data
