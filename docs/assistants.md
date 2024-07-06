# Local Assistants

The assistants API allows for database-backed assistants to be created and run fully local.

There are three base architectures:

- Chat: Just LLM
- Chat Retrieval/RAG
- Agent (RAG + Tools)

New agent architectures that include things like self-reflection, multi-agent collaboration, and complex control flows (eg. customer support) are implemented relatively easily using [LangGraph](https://langchain-ai.github.io/langgraph/).

## Assistant Configuration

The setup is unique in that it is meant to be easily modified as new agent architectures are introduced. Here is an example of what an assistant configuration might look like with the three base architectures:

```json
{
  "configurable": {
    "type": "agent",
    "type==agent/tools": [],
    "type==agent/interupt_before_action": true,
    "type==agent/agent_type": "GPT 3.5 Turbo",
    "type==agent/system_message": "You are a helpful assistant.",
    "type==agent/retrieval_description": "Can be used to look up information.",
    "type==chat_retrieval/system_message": "You are a helpful assistant.",
    "type==chatbot/llm_type": "GPT 3.5 Turbo",
    "type==chatbot/system_message": "You are a helpful assistant.",
    "type==chat_retrieval/llm_type": "GPT 3.5 Turbo"
  }
}
```

In this example, there are three assistant architectures: agent, chatbot, and chat_retrieval. The `type` value defines the architecture to be used for this assistant, in this case "agent", which tells the system to only pay attention to key/value pairs where `type == agent`. As such, the `configurable` object can be reduced to:

```json
{
  "configurable": {
    "type": "agent",
    "type==agent/tools": [],
    "type==agent/interupt_before_action": true,
    "type==agent/agent_type": "GPT 3.5 Turbo",
    "type==agent/system_message": "You are a helpful assistant.",
    "type==agent/retrieval_description": "Can be used to look up information."
  }
}
```

Some may find the keys in the `configurable` object peculiar. Although it may seem complex to wrap your head around at first, it actually simplifies things considerably as it allows for the assistant configuration to be bound to predefined schemas for each architecture while being able to scale as new LangGraph agent pipelines are added without having to support a continuously expanding assistants model.

## Tools

A small set of tools are currently available, with more tools planned:

- Vector Retrieval
- DuckDuckGo Search
- Search with Tavily
- DALL-E image generation
- Sem4.ai Action Server
- Connery action runner
- Arxiv
- YouSearch
- Kai.ai - Company filings and press releases
- Wikipedia
- PubMed

Tools are added to an assistant as an array of objects, like so:

```json
{
  "id": "retrieval",
  "type": "retrieval",
  "name": "Retrieval",
  "description": "Look up information in uploaded files.",
  "config": {}
}
```

### Creating New Tools
