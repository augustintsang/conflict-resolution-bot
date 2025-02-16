from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json

# Reuse the logic functions directly
from objective import generate_objective_logic, ObjectiveInput
from evaluate import evaluate_conversation_logic, EvaluateInput
from knowledge import knowledge_logic, KnowledgeInput

# Create a separate APIRouter for the streaming WebSocket endpoint
router = APIRouter()

@router.websocket("/ws_stream_insights")
async def ws_stream_insights(websocket: WebSocket):
    """
    A WebSocket endpoint that allows streaming partial conversation chunks.
    For each new chunk, we:
      1) Accumulate the conversation
      2) Generate updated "Objective" & "Evaluate"
      3) Use them to build knowledge queries
      4) Return partial results to the client
    """
    await websocket.accept()
    conversation_so_far = ""

    try:
        while True:
            # Receive a chunk of conversation text from the client
            chunk = await websocket.receive_text()
            conversation_so_far += " " + chunk  # accumulate text

            # 1) Objective
            objective_data = generate_objective_logic(
                ObjectiveInput(conversation=conversation_so_far)
            )

            # 2) Evaluate
            evaluate_data = evaluate_conversation_logic(
                EvaluateInput(conversation=conversation_so_far)
            )

            # 3) Build knowledge questions from the partial results
            questions_list = []
            for obj_item in objective_data:
                if "Objective" in obj_item:
                    questions_list.append(obj_item["Objective"])

            for eval_item in evaluate_data:
                if "Information_request" in eval_item:
                    questions_list.append(eval_item["Information_request"])

            # 4) If we have any new questions, run knowledge logic
            knowledge_data = []
            if questions_list:
                knowledge_data = knowledge_logic(KnowledgeInput(questions=questions_list))

            # Construct a partial result payload
            partial_result = {
                "Objective": objective_data,
                "Evaluate": evaluate_data,
                "knowledge": knowledge_data
            }

            # Send the updated partial result back to the client
            await websocket.send_text(json.dumps(partial_result))

    except WebSocketDisconnect:
        # The client disconnected from the WebSocket
        pass
