# objective.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import json
import weave
import re
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

#
# KNOWLEDGE MODELS
#
class KnowledgeInput(BaseModel):
    """
    Pydantic model for the knowledge endpoint request.
    Accepts multiple questions batched in an array.
    """
    questions: List[str] = ["How many stars are in the universe?"]

class KnowledgeOutput(BaseModel):
    """Pydantic model for a single line of processed knowledge with citations."""
    original_line: str
    clean_line: str
    citations: List[str]

class BatchedKnowledgeOutput(BaseModel):
    """Pydantic model for the batched output of the knowledge endpoint."""
    question: str
    results: List[KnowledgeOutput]

#
# Create a single FastAPI app instance
#
app = FastAPI()

#
# Initialize Weave for tracking
#
weave.init("objective-tracking")

def associate_citations_with_text(text: str, citations: List[str]):
    """
    Scans the text for bracketed references (e.g., [1], [2], etc.),
    and associates them with the corresponding entry in the `citations` list.
    
    :param text: The text containing bracketed references.
    :param citations: A list of citation URLs (list indices correspond to [1], [2], etc.).
    :return: A list of dictionaries, each containing:
             {
                 'original_line': The original line of text (with references),
                 'clean_line': The line with reference markers removed,
                 'citations': A list of citation URLs corresponding to the references
             }
    """
    # Split the text into lines
    lines = text.strip().split('\n')
    
    # This list will hold the result for each line
    line_citations = []
    
    for line in lines:
        # Find all bracketed references like [1], [2], [3], etc.
        refs = re.findall(r'\[(\d+)\]', line)
        
        # Remove the bracket references from the line to create a "clean" version
        clean_line = re.sub(r'\[\d+\]', '', line).strip()
        
        # Map each reference (e.g., "1") to its citation in the list
        associated_citations = []
        for ref in refs:
            index = int(ref) - 1  # bracketed refs are 1-based; Python lists are 0-based
            if 0 <= index < len(citations):
                associated_citations.append(citations[index])
            else:
                associated_citations.append(f"Unknown citation index: {ref}")
        
        line_citations.append({
            'original_line': line,
            'clean_line': clean_line,
            'citations': associated_citations
        })
    
    return line_citations

#
# ENDPOINTS
#

@weave.op()
@app.post("/generate_objective", response_model=List[ObjectiveOutput])
def generate_objective(input_data: ObjectiveInput):
    """
    This endpoint generates a JSON array matching the schema:
      [
        {
          "Objective": "some string"
        }
      ]
    It takes a conversation string as input, then uses the Sambanova model
    to extract the conversation's objective(s).
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

    # Extract the generated text from the first choice and parse it as JSON.
    try:
        content = response["choices"][0]["message"]["content"]
        objectives = json.loads(content)
    except Exception as e:
        raise ValueError("Failed to parse model output as a valid JSON array.") from e

    return objectives

@weave.op()
@app.post("/knowledge", response_model=List[BatchedKnowledgeOutput])
def get_knowledge(input_data: KnowledgeInput):
    """
    This endpoint returns knowledge processing results.
    It accepts multiple questions and, for each one, uses a completion from the Perplexity model 
    to answer the question, then processes the answer to associate citations with each line of text.
    """
    batched_results = []
    for question in input_data.questions:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an artificial intelligence assistant and you need to "
                    "engage in a helpful, detailed, polite conversation with a user."
                ),
            },
            {
                "role": "user",
                "content": question,
            },
        ]
        
        response = completion(
            model="perplexity/sonar-pro",
            messages=messages
        )
        
        # Extract the text answer and the citations from the response.
        try:
            text = response["choices"][0]["message"]["content"]
            citations = response["citations"]
        except Exception as e:
            raise ValueError("Failed to parse the model response for the knowledge query.") from e
        
        results = associate_citations_with_text(text, citations)
        batched_results.append({
            "question": question,
            "results": results
        })
    
    return batched_results


#
# IMPORTANT: Import `evaluate` here so that /evaluate_conversation is also attached
# to the same 'app' instance. This must happen AFTER app = FastAPI() is defined.
#
import evaluate  # noqa: E402

# If running this file directly: `python objective.py`
if __name__ == "__main__":
    uvicorn.run("objective:app", host="0.0.0.0", port=8000, reload=False)
