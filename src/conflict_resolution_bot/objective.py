# objective.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import json
import uvicorn
from litellm import completion

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
    It takes a conversation string as input, then uses the Sambanova model to extract the conversation's objective(s).
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

    # Prepare messages with a system prompt and the user-provided conversation.
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": conversation}
    ]

    # Use litellm's completion to generate the objective using the Sambanova model.
    response = completion(
        model="sambanova/Meta-Llama-3.1-8B-Instruct",
        messages=messages,
        response_format={"type": "json_object"}
    )

    # Extract the generated text from the first choice.
    try:
        content = response["choices"][0]["message"]["content"]
        # Parse the JSON output from the generated text.
        objectives = json.loads(content)
    except Exception as e:
        raise ValueError("Failed to parse model output as a valid JSON array.") from e

    return objectives

#
# IMPORTANT: Import `evaluate` here so that /evaluate_conversation is also attached
# to the same 'app' instance. This must happen AFTER app = FastAPI() is defined.
#
import evaluate  # noqa: E402

# If running this file directly: `python objective.py`
if __name__ == "__main__":
    uvicorn.run("objective:app", host="0.0.0.0", port=8000, reload=False)
