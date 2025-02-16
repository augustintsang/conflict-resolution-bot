# main.py

from fastapi import FastAPI
from typing import List
from pydantic import BaseModel
import weave

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


# If you run this file directly:
if __name__ == "__main__":
    import uvicorn
    # Example run:
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
