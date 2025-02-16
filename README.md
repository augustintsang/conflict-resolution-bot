

to run gemini, run:

```
poetry build
```


Run the web server:
```
poetry run python src/conflict_resolution_bot/objective.py
```


Get "Objective":
```
curl -X POST "http://localhost:8000/generate_objective" \
    -H "Content-Type: application/json" \
    -d '{
      "conversation": "Steve: Alright, so we all agree on the idea—an AI-powered restaurant reservation agent. It checks availability, books a table, even suggests options based on user preferences.\nAshwini: Yeah, and it should be able to call or message restaurants that don’t have an online system.\nJose: Love it. So for the agent framework, LlamaIndex seems like a no-brainer. It’s one of the sponsors, and it’s solid for retrieval-augmented generation.\nAshwini: Agreed. Plus, we get points for using sponsor tools. Let’s lock that in.\n(They nod, moving on to the next decision.)\nSteve: Now, the LLM. Gemini’s a sponsor, so we’d benefit from using it. But OpenAI o1 is... well, OpenAI o1. It’s top-tier.\nJose: Yeah, but we’re optimizing for both performance and hackathon perks. Gemini’s not bad—it gives decent results, and it keeps us in good standing with the event judges.\nAshwini: True, but we’re not required to use sponsor tools. If OpenAI’s going to get us better responses, wouldn’t that be worth it?\nSteve: Maybe. But is the improvement enough to justify skipping a sponsor?\n(They pause, unsure. Then, Jose pivots to another key issue.)\nJose: Okay, what about connecting to the web? We need real-time data—restaurant availability, location details, even user reviews.\nAshwini: AgentQL is a sponsor, so it’d be cheaper for us. But I have no clue how tricky it is to implement.\nSteve: Yeah, I haven’t seen many people using it yet. On the other hand, Perplexity API is reliable. More expensive, but we know it works well.\nJose: So do we go for ease-of-use and proven reliability with Perplexity? Or do we save money and earn sponsor points with AgentQL?\nAshwini: That’s the problem. I don’t know how long AgentQL would take to set up. If it’s a pain, we could waste a lot of time.\nSteve: And if we pick OpenAI o1 for the LLM, plus Perplexity for web search, that’s two major non-sponsor choices. Could hurt us.\nJose: But if the quality is better, maybe that’s worth the risk?\nAshwini: We don’t have enough info. We need to check how hard AgentQL is to implement fast.\nSteve: Yeah, and we need to decide if Gemini is “good enough” or if OpenAI o1 is worth breaking from the sponsor incentives.\n(They look at each other, still unsure. The clock is ticking, and they need to make a call soon.)\nJose: Okay, let’s do some quick tests, maybe ask around. We need to settle this now."
    }'
```