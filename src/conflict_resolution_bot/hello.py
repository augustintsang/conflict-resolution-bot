from llama_index.llms.gemini import Gemini

llm = Gemini(
    model="models/gemini-2.0-flash-thinking-exp",
    # api_key="some key",  # uses GOOGLE_API_KEY env var by default
)

resp = llm.complete("Write a poem about a magic backpack")

print(resp)