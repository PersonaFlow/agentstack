# Local Assistants API

The assistants API allows for database-backed assistants to be created and run fully locally.

Current architectures:

- Chat: Just LLM
- Chat Retrieval (RAG)
- Agent (RAG + Tools)
- Corrective RAG Agent (in progress)

New agent architectures that include things like self-reflection, multi-agent collaboration, and complex control flows (eg. customer support) are implemented relatively easily using [LangGraph](https://langchain-ai.github.io/langgraph/).

## Assistant Configuration

The setup is unique in that it is meant to be easily modified as new agent architectures are introduced. Here is an example of what an assistant configuration might look like with the three base architectures:

```json
{
  "configurable": {
    "type": "agent",
    "type==agent/tools": [],
    "type==agent/interupt_before_action": true,
    "type==agent/agent_type": "GPT 4o Mini",
    "type==agent/system_message": "You are a helpful assistant.",
    "type==agent/retrieval_description": "Can be used to look up information.",
    "type==chat_retrieval/system_message": "You are a helpful assistant.",
    "type==chatbot/llm_type": "GPT 4o Mini",
    "type==chatbot/system_message": "You are a helpful assistant.",
    "type==chat_retrieval/llm_type": "GPT 4o Mini"
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
    "type==agent/agent_type": "GPT 4o Mini",
    "type==agent/system_message": "You are a helpful assistant.",
    "type==agent/retrieval_description": "Can be used to look up information."
  }
}
```

Some may find the keys in the `configurable` object peculiar. Although it may seem complex to wrap your head around at first, it actually simplifies things considerably as it allows for the assistant configuration to be bound to predefined schemas for each architecture while being able to scale as new LangGraph agent pipelines are added without having to support a continuously expanding assistants model.

However, it is important to note that these type annotations are _not_ required. An assistant configuration that is loaded into the run manager will still work without them as long as the type is specified, ie:

```json
{
  "configurable": {
    "type": "agent",
    "tools": [],
    "interupt_before_action": true,
    "agent_type": "GPT 4o Mini",
    "system_message": "You are a helpful assistant.",
    "retrieval_description": "Can be used to look up information."
  }
}
```

## Tools

A large focus has been placed on knowledge base RAG that is high quality and easily configurable, so a small set of tools are currently available, with more tools planned:

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

Tools are added to an assistant as an array of objects. The `config` field is where the tool-specific configuration is stored. For example, you can set options like the encoder configuration, rerank and the vector database index/collection name to use. If you are using multiple vector database, you can also specify the vector database that should be used by the retrieval tool as well.


```json
"tools": [
  {
      "type": "retrieval",
      "description": "Look up information in uploaded files.",
      "name": "Retrieval",
      "config": {
          "encoder": {
              "provider": "ollama",
              "dimensions": 384, 
              "encoder_model": "all-minilm"
          }, 
          "vector_database": {
            "type": "qdrant",
            "config": {
              "host": "http://localhost:6333",
              "api_key": "123456789"
            }
          },
          "enable_rerank": false,
          "index_name": "test"
      },
      "multi_use": false 
  }
],
```
Notes:
- The retrieval config is a means of overriding the defaults set via environment variables. 
- Retrieval and action server are the only tools that currently use the config field.
- `multi-use` is for tools that are mult-purpose, such as the Sem4.ai Action Server or Connery. 


