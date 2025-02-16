# main.py

from fastapi import FastAPI
from typing import List
from pydantic import BaseModel
import weave
import json
from litellm import completion

# Import the existing app
from app import app

# Import the logic-only functions (no circular import, because these don't import `app`)
from objective import generate_objective_logic, ObjectiveInput
from evaluate import evaluate_conversation_logic, EvaluateInput
from knowledge import knowledge_logic, KnowledgeInput

#
# Combined Data Models
#
class CombinedInput(BaseModel):
    conversation: str

class CombinedOutput(BaseModel):
    Objective: list
    Evaluate: list
    knowledge: list

class UIInsightsOutput(BaseModel):
    Objective: list
    insights: list

weave.init('hackathon-example')

#
# Combined Endpoint
#
@app.post("/combined_insights", response_model=CombinedOutput)
def combined_insights(input_data: CombinedInput):
    """
    This endpoint:
      1) Calls 'generate_objective_logic'
      2) Calls 'evaluate_conversation_logic'
      3) Feeds both outputs into 'knowledge_logic'
      4) Returns a JSON with "Objective", "Evaluate", and "knowledge"
    """

    # 1) Objective
    objective_data = generate_objective_logic(
        ObjectiveInput(conversation=input_data.conversation)
    )

    # 2) Evaluate
    evaluate_data = evaluate_conversation_logic(
        EvaluateInput(conversation=input_data.conversation)
    )

    # 3) Build knowledge questions from the objective & evaluate
    questions_list: List[str] = []

    for obj_item in objective_data:
        if "Objective" in obj_item:
            questions_list.append(obj_item["Objective"])

    for eval_item in evaluate_data:
        if "Information_request" in eval_item:
            questions_list.append(eval_item["Information_request"])

    # If we have no questions, knowledge_logic would return empty
    knowledge_data = knowledge_logic(KnowledgeInput(questions=questions_list))

    return {
        "Objective": objective_data,
        "Evaluate": evaluate_data,
        "knowledge": knowledge_data
    }

#
# UI Insights Endpoint
#
@app.post("/ui_insights", response_model=UIInsightsOutput)
def UI_insights(input_data: CombinedInput):
    """
    This endpoint:
      1) Calls 'generate_objective_logic'
      2) Calls 'evaluate_conversation_logic'
      3) Feeds both outputs into 'knowledge_logic'
      4) Calls an additional sambanova call to summarise these results into a single JSON object
         with the key 'insights' and a value that is a string detailing the most prioritized ideas.
      5) Returns a JSON with keys "objectives" and "insights".
    """
    # For demonstration purposes, assume that input_data is available in the request scope.
    # In practice, you might change this to a POST endpoint that receives a request body.
    # Here, we assume 'input_data.conversation' is provided.
    
    # 1) Objective
    objective_data = generate_objective_logic(
        ObjectiveInput(conversation=input_data.conversation)
    )

    # 2) Evaluate
    evaluate_data = evaluate_conversation_logic(
        EvaluateInput(conversation=input_data.conversation)
    )

    # 3) Build knowledge questions from the objective & evaluate outputs
    questions_list: List[str] = []
    for obj_item in objective_data:
        if "Objective" in obj_item:
            questions_list.append(obj_item["Objective"])
    for eval_item in evaluate_data:
        if "Information_request" in eval_item:
            questions_list.append(eval_item["Information_request"])

    # Get knowledge data based on collected questions
    knowledge_data = knowledge_logic(KnowledgeInput(questions=questions_list))

    # 4) Summarise the combined data for frontend insights.
    system_prompt = """
    You are an assistant tasked with summarising details from a discussion.
    
    Identify and prioritise the key ideas and insights for each choice raised in the discussion.

    Output a valid JSON object with 2 keys "objective", "insights" whose value is a string summary of the possible choices and their respective insights.
    
    The output:

    - MUST be valid JSON conforming to the schema below:
      [
        {
          "Objective": "some string"
          "insights": "some string"
        }
      ]
    - MUST NOT include additional commentary or formatting.
    """

    # Aggregate all extracted data into a string for summarisation.
    aggregated_content = json.dumps({
        "Objective": objective_data,
        "evaluations": evaluate_data,
        "knowledge": knowledge_data
    })

    insights_response = completion(
        model="sambanova/Meta-Llama-3.1-8B-Instruct",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": aggregated_content}
        ],
        response_format={"type": "json_object"}
    )

    try:
        insights_content = insights_response["choices"][0]["message"]["content"]
        insights_json = json.loads(insights_content)
        insights = insights_json.get("insights", "")
    except Exception as e:
        raise ValueError("Failed to parse insights summary output as valid JSON object.") from e

    # 5) Return final JSON for the frontend
    return {
        "Objective": objective_data,
        "insights": insights
    }



# If you run this file directly:
if __name__ == "__main__":
    import uvicorn
    # Example run:
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
