from google import genai
from pydantic import BaseModel, TypeAdapter
import os

# 1) Define a Pydantic model matching your desired JSON schema.
class InfoItem(BaseModel):
    Objective: str

# 2) Create the system prompt telling the model exactly what to do.
system_prompt = """
You are reviewing a conversation among multiple participants.

Your goal is to produce a JSON array containing the objective of the conversation.

The output:
- MUST be valid JSON conforming to the schema below:
  [
    {
      "Objective": "some string"
    },
    ...
  ]
- MUST NOT include additional commentary or formatting.

For example, if they discussed “Crew AI,” a valid object might be:
{
  "Objective": "Create a cookie recipe"
}

Return ONLY the JSON array, nothing else. 
"""

# 3) Example conversation that you'll pass in as "contents".
conversation = """
Steve: Alright, so we all agree on the idea—an AI-powered restaurant reservation agent. It checks availability, books a table, even suggests options based on user preferences.
Ashwini: Yeah, and it should be able to call or message restaurants that don’t have an online system.
Jose: Love it. So for the agent framework, LlamaIndex seems like a no-brainer. It’s one of the sponsors, and it’s solid for retrieval-augmented generation.
Ashwini: Agreed. Plus, we get points for using sponsor tools. Let’s lock that in.
(They nod, moving on to the next decision.)
Steve: Now, the LLM. Gemini’s a sponsor, so we’d benefit from using it. But OpenAI o1 is... well, OpenAI o1. It’s top-tier.
Jose: Yeah, but we’re optimizing for both performance and hackathon perks. Gemini’s not bad—it gives decent results, and it keeps us in good standing with the event judges.
Ashwini: True, but we’re not required to use sponsor tools. If OpenAI’s going to get us better responses, wouldn’t that be worth it?
Steve: Maybe. But is the improvement enough to justify skipping a sponsor?
(They pause, unsure. Then, Jose pivots to another key issue.)
Jose: Okay, what about connecting to the web? We need real-time data—restaurant availability, location details, even user reviews.
Ashwini: AgentQL is a sponsor, so it’d be cheaper for us. But I have no clue how tricky it is to implement.
Steve: Yeah, I haven’t seen many people using it yet. On the other hand, Perplexity API is reliable. More expensive, but we know it works well.
Jose: So do we go for ease-of-use and proven reliability with Perplexity? Or do we save money and earn sponsor points with AgentQL?
Ashwini: That’s the problem. I don’t know how long AgentQL would take to set up. If it’s a pain, we could waste a lot of time.
Steve: And if we pick OpenAI o1 for the LLM, plus Perplexity for web search, that’s two major non-sponsor choices. Could hurt us.
Jose: But if the quality is better, maybe that’s worth the risk?
Ashwini: We don’t have enough info. We need to check how hard AgentQL is to implement fast.
Steve: Yeah, and we need to decide if Gemini is “good enough” or if OpenAI o1 is worth breaking from the sponsor incentives.
(They look at each other, still unsure. The clock is ticking, and they need to make a call soon.)
Jose: Okay, let’s do some quick tests, maybe ask around. We need to settle this now.
"""

# 4) Initialize the genai client. Replace "YOUR_API_KEY" with your real key.
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# 5) Generate the content with forced JSON extraction & validation.
response = client.models.generate_content(
    model="models/gemini-2.0-flash",
    contents=conversation,      # The conversation or "user" message
    config={
        "response_mime_type": "application/json",
        "system_instruction": system_prompt,
        # Let genai parse the response into a list of InfoItem objects.
        "response_schema": list[InfoItem],
        "temperature": 0
    }
)

# 6) Print the raw JSON text (already guaranteed to match your schema).
print(response.text)