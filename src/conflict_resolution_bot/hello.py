from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import asyncio
import os


# Instantiate your custom embedding model (change the model_name as needed)
custom_embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")

# Create a RAG tool using LlamaIndex
documents = SimpleDirectoryReader("src/conflict_resolution_bot/data").load_data()

# Instantiate your custom embedding model (change the model_name as needed)
custom_embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")

# Create your index and explicitly pass the custom embedding model
index = VectorStoreIndex.from_vector_store(
    vector_store,
    embed_model=custom_embed_model,
)

query_engine = index.as_query_engine()


async def search_documents(query: str) -> str:
    """Useful for answering natural language questions about an personal essay written by Paul Graham."""
    response = await query_engine.aquery(query)
    return str(response)

system_prompt = """
Analyze the following meeting transcript and extract the 
primary objective or collective goal discussed. Provide your response in the following JSON format:

{
  "objective": "<extracted objective>",
  "key_points": "<extracted key points>"
}
"""

# Create an enhanced workflow with both tools
agent = AgentWorkflow.from_tools_or_functions(
    [search_documents],
    llm=Gemini(model="gemini-1.5-flash-002"),
    system_prompt=system_prompt,
)


# Now we can ask questions about the documents or do calculations
async def main():
    response = await agent.run(
        "What did the author do in college? Also, what's 7 * 8?"
    )
    print(response)


# Run the agent
if __name__ == "__main__":
    asyncio.run(main())