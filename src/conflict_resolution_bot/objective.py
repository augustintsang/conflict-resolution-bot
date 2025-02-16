import json
from typing import List
from pydantic import BaseModel
from litellm import completion
import weave
import os

# Import the shared app to expose endpoint routes
from app import app

#
# Data Models
#
class ObjectiveInput(BaseModel):
    conversation: str

class ObjectiveOutput(BaseModel):
    Objective: str

#
# Endpoint & Logic
#
@app.post("/generate_objective", response_model=List[ObjectiveOutput])
@weave.op()
def generate_objective_endpoint(input_data: ObjectiveInput):
    """
    This endpoint returns a JSON array:
      [ { "Objective": "some string" } ]
    derived from the conversation string.
    """
    return generate_objective_logic(input_data)

def generate_objective_logic(input_data: ObjectiveInput) -> List[dict]:
    """
    Plain Python function that does the real work.
    Return e.g. [ { "Objective": "some string" }, ... ]
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
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": input_data.conversation}
    ]

    # Example usage of litellm
    response = completion(
        model="sambanova/Meta-Llama-3.1-8B-Instruct",
        messages=messages,
        response_format={"type": "json_object"}
    )

    try:
        content = response["choices"][0]["message"]["content"]
        objectives = json.loads(content)
    except Exception as e:
        raise ValueError("Failed to parse model output as valid JSON array.") from e

    # `objectives` should be a list of { "Objective": ... }
    return objectives
