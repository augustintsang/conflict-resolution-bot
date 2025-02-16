# objective.py

import json
from typing import Dict
from pydantic import BaseModel
from litellm import completion
import weave
import os

from app import app  # Import the shared app (no circular import)
# (Don't import evaluate.py or knowledge.py here to avoid circular import)

#
# Data Models
#
class StakeholderInput(BaseModel):
    conversation: str

class StakeholderDetails(BaseModel):
    motivations_values: str
    opinions: str

#
# Endpoint & Logic
#
@app.post("/generate_stakeholders", response_model=Dict[str, StakeholderDetails])
@weave.op()
def generate_stakeholders_endpoint(input_data: StakeholderInput):
    """
    This endpoint returns a JSON object where each key is a participant's name,
    and the value is an object containing:
      - "motivations_values": Their combined motivations and values.
      - "opinions": Their opinions on the problem being discussed.
    """
    return generate_stakeholders_logic(input_data)

def generate_stakeholders_logic(input_data: StakeholderInput) -> Dict[str, dict]:
    """
    Process the conversation and return a JSON object with stakeholder details.

    The output must be valid JSON formatted like this:
    {
      "Alice": {
         "motivations_values": "Alice's combined statement about her motivations and values",
         "opinions": "Alice's opinions on the problem"
      },
      "Bob": {
         "motivations_values": "Bob's combined statement about his motivations and values",
         "opinions": "Bob's opinions on the problem"
      }
    }

    Do not include any extra commentary or formatting.
    """
    system_prompt = """
    You are reviewing a conversation among multiple participants.
    Your goal is to identify all stakeholders in the conversation and, for each, extract:
      - Their combined motivations and values.
      - Their opinions on the problem being discussed.
    
    The output must be a valid JSON object where each key is the name of a stakeholder and each value is an object with two keys:
      "motivations_values": containing the stakeholder's motivations and values,
      "opinions": containing the stakeholder's opinions on the problem.
    
    For example:
    {
      "Alice": {
         "motivations_values": "Alice's combined statement about her motivations and values",
         "opinions": "Alice's opinions on the problem"
      },
      "Bob": {
         "motivations_values": "Bob's combined statement about his motivations and values",
         "opinions": "Bob's opinions on the problem"
      }
    }
    
    Do not include any extra commentary or formatting.
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": input_data.conversation}
    ]

    response = completion(
        model="sambanova/Meta-Llama-3.1-8B-Instruct",
        messages=messages,
        response_format={"type": "json_object"}
    )

    try:
        content = response["choices"][0]["message"]["content"]
        stakeholders = json.loads(content)
    except Exception as e:
        raise ValueError("Failed to parse model output as valid JSON object.") from e

    return stakeholders
