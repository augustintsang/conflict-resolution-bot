from llama_index.llms.gemini import Gemini
from llama_index.core.bridge.pydantic import WithJsonSchema

# Define the JSON schema you want to enforce.
json_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "topic": {"type": "string"},
            "Information_request": {"type": "string"}
        },
        "required": ["topic", "Information_request"]
    }
}

# Create the system prompt telling the model exactly what to do.
system_prompt = """
You are reviewing a conversation among multiple participants.

Your goal is to produce a JSON array containing each piece of information 
the team needs to look up or clarify to resolve the conversation. 

The output:
- MUST be valid JSON conforming to the schema below:
  [
    {
      "topic": "some string",
      "Information_request": "some string"
    },
    ...
  ]
- MUST NOT include additional commentary or formatting.

For example, if they discussed “Crew AI,” a valid object might be:
{
  "topic": "Crew AI",
  "Information_request": "Is Crew AI the best framework?"
}

Return ONLY the JSON array, nothing else.
"""

# Instantiate the Gemini LLM, specifying the JSON schema wrapper.
llm = Gemini(
    system_prompt=system_prompt,
    model="models/gemini-2.0-flash-thinking-exp",
    messages_to_prompt=WithJsonSchema(json_schema=json_schema)
)

# Now call .complete with the conversation text as the user message:
conversation = """
Jessica: Okay, so we all like the idea of an AI agent that orders groceries on Instacart. Crew AI seems like the best framework, yeah?
John: Yeah, Crew AI’s built for multi-agent workflows, and I think it gives us a solid starting point. We don’t have to build everything from scratch.
Guilio: I’m in. Crew AI is solid, and honestly, we’ll need something structured if we want this to function well within 24 hours.
Jessica: Cool. That’s locked in. Now, about data storage… do we save user queries for personalization?
John: Do we need to, though? I mean, for a V1, do users really care about seeing past orders? Instacart already has that built-in.
Guilio: Yeah, but this is where we can go big. If we store order history and train the AI on preferences, we make the agent smarter. ApertureDB is a sponsor. If we use it, we might get extra points.
John: But it adds complexity. We’d have to integrate the database, test it, and make sure it doesn’t slow us down. A simpler 3rd party DB or even just skipping this feature could save us hours.
Guilio: And make our agent feel like every request is from scratch. That’s not competitive. I’m here to win, man. If we half-bake this, what’s the point?
John: Not everything needs to be a moonshot. A clean, functional AI that places orders well is more important than a clunky, overly ambitious one.
Guilio: So what, we just settle for basic? If we don’t push it, someone else will.
Jessica: Okay, let’s cool it for a sec. We’re at an impasse. Storing data could be powerful, but it might slow us down. Maybe we need more info—how hard is an ApertureDB integration? Is there a way to keep it lightweight?
John: If we find a way to store past orders without bloating the scope, I’m open to it. But if it makes us rush everything else, I’m against it.
Guilio: And I don’t want to waste time on a product that won’t even stand out.
Jessica: Sounds like we need to dig into what’s feasible fast. Let’s check ApertureDB’s docs and maybe ask around. If it’s a nightmare, we pivot.
John: Yeah… fine. But if it’s too much, we don’t force it.
Guilio: Agreed—if we’re sure it’s too much.
Jessica: Alright, let’s research. Five-minute break, then regroup?
"""

response = llm.complete(conversation)

print(response)
