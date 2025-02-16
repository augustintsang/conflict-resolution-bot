export interface MarkdownContent {
  filename: string;
  content: string;
}

// Since we can't use fs in the browser, we'll hardcode the guidelines
export function getGuidelines(): MarkdownContent[] {
  return [
    {
      filename: 'conversation.md',
      content: `# Tools availabe in the Hackathon

## Google DeepMind (Gemini API)  
- **Overview:** Google DeepMind offers the **Gemini** model family – large multimodal AI models (Gemini 2.0 variants) accessible via an API. Developers can use Google AI Studio or SDKs to integrate Gemini into applications.  
- **Key Features:** Supports **text, vision, and audio** inputs/outputs natively, handles **long context** (millions of tokens), offers **tool use and code execution**, structured output modes like JSON and **function calling**, and supports fine-tuning.  
- **Use Cases:** Advanced **chatbots and assistants**, coding copilots, and content generators. Gemini's multimodal and reasoning abilities enable **agentic applications**, such as AI agents that can research, analyze, and execute tasks autonomously.

## SambaNova  
- **Overview:** **SambaNova Cloud** provides fast inference on open-source models, powered by SambaNova's SN40L AI chip. It provides hosted access to large language and vision models with an **API compatible with OpenAI's**, making integration seamless.  
- **Key Features:** Supports a range of **open-source LLMs** (e.g., Llama 3.x, Qwen family), **multimodal vision models**, an **audio model** for speech reasoning, **function calling and JSON output**, and **RAG (Retrieval Augmented Generation) integration**.  
- **Use Cases:** High-performance inference of **open models**, multimodal AI applications (image analysis, audio transcription), and **enterprise Q&A systems** leveraging RAG.

## Activeloop (Deep Lake)  
- **Overview:** **Deep Lake** is a data lakehouse for AI, functioning as a **vector database** for embeddings and multimodal data management. It allows storing and querying text, images, audio, and video in a unified way.  
- **Key Features:** High-performance **Tensor Query Language (TQL)**, **hybrid search (keyword + vector search)**, **multi-modal embeddings**, and **fast semantic search**.  
- **Use Cases:** **Retrieval-augmented QA systems**, **multi-modal assistants**, and **enterprise knowledge search** (e.g., indexing documents, images, and transcripts for AI-powered queries).

## Stytch  
- **Overview:** **Stytch** is a developer platform for authentication, security, and user identity, providing essential services for **AI applications that require secure user management**.  
- **Key Features:** **Passwordless authentication**, **B2B auth (SAML SSO, RBAC, OAuth)**, **Connected Apps for external integrations**, and **fraud prevention**.  
- **Use Cases:** **User authentication for AI applications**, enterprise AI SaaS, and **secure access control** for generative AI services.

## VESSL AI (Platform & Hyperpocket)  
- **Overview:** **VESSL AI** is a cloud platform for **training, deploying, and orchestrating AI models**. It also offers **Hyperpocket**, an open-source interface for AI agents to integrate external tools and APIs easily.  
- **Key Features:** **GPU-accelerated AI workloads**, **serverless model deployment**, **workflow automation**, and **agent tool integration with authentication** via Hyperpocket.  
- **Use Cases:** **AI model fine-tuning**, **LLM deployment as web services**, and **autonomous AI agents** with multi-step workflows.

## LlamaIndex  
- **Overview:** **LlamaIndex** is a framework for building **data-driven LLM applications**, often used for **Retrieval Augmented Generation (RAG)**.  
- **Key Features:** **Data connectors**, **multiple indexing methods (vector, keyword, graph)**, **query planning**, **prompt engineering tools**, and **integration with LangChain and Pinecone**.  
- **Use Cases:** **Enterprise Q&A bots**, **multi-modal search systems**, and **knowledge-enhanced AI applications**.

## Together AI  
- **Overview:** **Together AI** provides cloud-based inference and fine-tuning for **open-source generative models**.  
- **Key Features:** **Inference API for LLaMA, Mistral, Code Llama**, **image generation (Stable Diffusion, Flux)**, **function calling**, **custom model hosting**, and **fine-tuning tools**.  
- **Use Cases:** **Chatbots, assistants, generative image apps, text-to-speech applications**, and **real-time AI services with low latency**.

## Fly.io  
- **Overview:** **Fly.io** is a cloud hosting platform that specializes in **edge deployment**, making it easy to **deploy AI-powered web services or APIs globally**.  
- **Key Features:** **Developer-friendly deployment**, **global autoscaling**, **managed databases (Postgres, Redis)**, and **low-latency infrastructure**.  
- **Use Cases:** **Hosting AI inference endpoints**, **deploying AI-powered APIs**, and **scalable generative AI applications**.

## ApertureData (ApertureDB)  
- **Overview:** **ApertureDB** is a **unified multimodal database** combining a **vector search engine**, **knowledge graph**, and **structured data storage** for AI applications.  
- **Key Features:** **Vector search**, **multi-modal data storage**, **knowledge graph capabilities**, and **high-performance query engine**.  
- **Use Cases:** **Enterprise AI knowledge bases**, **computer vision data management**, and **AI-driven recommendation systems**.

## ZenML  
- **Overview:** **ZenML** is an **MLOps framework** that helps transition ML projects from research to production, focusing on **LLMOps (Large Language Model Operations)**.  
- **Key Features:** **Pipeline orchestration**, **infrastructure-agnostic ML workflows**, **integrations with LLM tools**, and **continuous deployment for AI models**.  
- **Use Cases:** **Productionizing LLM-powered apps**, **managing AI pipelines**, and **automating model retraining workflows**.

## HappyRobot  
- **Overview:** **HappyRobot** is a platform for **AI-powered voice and text automation**, enabling **AI-driven customer support and voice agents**.  
- **Key Features:** **Voice agent infrastructure**, **workflow automation**, **multi-channel support (email, SMS, calls)**, and **third-party integrations**.  
- **Use Cases:** **Automated customer support**, **AI-powered sales and outreach calls**, and **HR/IT helpdesk automation**.

## Agno (Agent Framework)  
- **Overview:** **Agno** is an open-source **AI agent framework** for developing **multi-agent systems** with **LLM integration, memory management, and tool usage**.  
- **Key Features:** **Tool integration**, **multi-agent collaboration**, **RAG support**, and **task delegation workflows**.  
- **Use Cases:** **Custom AI assistants**, **autonomous task agents**, and **multi-agent collaborations** for research, finance, and automation.

## AgentQL  
- **Overview:** **AgentQL** is an **AI-powered query language** that enables **web automation, data extraction, and AI-driven browsing**.  
- **Key Features:** **Natural language selectors**, **resilient self-healing web queries**, **structured JSON output**, and **automation workflows**.  
- **Use Cases:** **AI-powered web scraping**, **autonomous browsing agents**, and **automated form-filling or website interactions**.`
    },
    {
      filename: 'technical.md',
      content: `# Prizes in the hackathon

$15,800+ in prizes+ other prizes
Best use of Senso.ai
1 winner
- $500 in credits to winning team

Best use of Deep Lake (Activeloop)
1 winner
Meta Quest 3S 128GB + $1000 in Activeloop Deep Lake Credits for the team

Best use of Stytch
$1,500 in cash
2 winners
$1k for first place team + Rayban Meta glasses per person on the team

$500 for 2nd place team

Best use of Vessl AI
$300 in cash
1 winner
300$ amazon gift card + $500 Vessl Cloud credits for the team

Best use of LlamaIndex
$1,000 in cash
1 winner
$1000 for the winning team

Best Project Built on Together AI
1 winner
$2,500 in Together API credits for the team

Best use of Fly.io
1 winner
$5k in credits for the team

Best use of apertureDB (ApertureData)
$1,000 in cash
1 winner
$1,000 for the team with best use of ApertureDB + 2 months of ApertureDB Cloud Basic Tier free per team member + featured blog post

Best use of ZenML
$500 in cash
1 winner
$7K in ZenML Pro credits and $500 cash for the team

Best use of HappyRobot
$500 in cash
1 winner
$500 cash for the team + $2,000 in credits

Best use of Agno
$3,000 in cash
3 winners
1st: $1500 cash for the team
2nd: $1000 cash for the team
3rd: $500 cash for the team

Best use of Agent QL (Tiny Fish)
$500 in cash
1 winner
$500 cash for the team

Best use of Sambanova
3 winners
$2K in credits for 1st place team
$1K in credits for 2nd place team
$500 in credits for 3rd place team

Best use of Weave (W&B)
2 winners
$5k in Weave Pro subscription for the team, 1 e-scooter per team ONLY`
    }
  ];
}