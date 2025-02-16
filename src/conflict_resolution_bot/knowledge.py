# knowledge.py
import json
import re
from typing import List
from pydantic import BaseModel
from litellm import completion
import weave

from app import app

#
# Data Models
#
class KnowledgeInput(BaseModel):
    questions: List[str]

class KnowledgeOutput(BaseModel):
    original_line: str
    clean_line: str
    citations: List[str]

class BatchedKnowledgeOutput(BaseModel):
    question: str
    results: List[KnowledgeOutput]


#
# Endpoint
#
@app.post("/knowledge", response_model=List[BatchedKnowledgeOutput])
def knowledge_endpoint(input_data: KnowledgeInput):
    """
    Accepts multiple questions, uses Perplexity model to answer each question.
    Then associates citations with the lines.
    """
    return knowledge_logic(input_data)


#
# Logic
#
def knowledge_logic(input_data: KnowledgeInput) -> List[dict]:
    batched_results = []
    for question in input_data.questions:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an artificial intelligence assistant. "
                    "Engage in a helpful, detailed conversation with a user."
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

        try:
            text = response["choices"][0]["message"]["content"]
            citations = response["citations"]
        except Exception as e:
            raise ValueError("Failed to parse the model response.") from e

        results = associate_citations_with_text(text, citations)
        batched_results.append({
            "question": question,
            "results": results
        })

    return batched_results


def associate_citations_with_text(text: str, citations: List[str]):
    lines = text.strip().split('\n')
    line_citations = []

    for line in lines:
        refs = re.findall(r'\[(\d+)\]', line)
        clean_line = re.sub(r'\[\d+\]', '', line).strip()

        associated_citations = []
        for ref in refs:
            idx = int(ref) - 1
            if 0 <= idx < len(citations):
                associated_citations.append(citations[idx])
            else:
                associated_citations.append(f"Unknown citation index: {ref}")

        line_citations.append({
            "original_line": line,
            "clean_line": clean_line,
            "citations": associated_citations
        })

    return line_citations
