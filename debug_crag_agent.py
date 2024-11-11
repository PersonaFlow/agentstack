#!/usr/bin/env python3
"""
Debug script for testing the configurable agent.
Place this file in your project root directory and run it from there.
"""

import os
import sys
import uuid
import asyncio
import json
import argparse
from typing import Optional
import structlog
from dotenv import load_dotenv
from langchain.schema.messages import HumanMessage
from psycopg_pool import AsyncConnectionPool

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from stack.app.core.datastore import initialize_checkpointer, initialize_db, cleanup_db
from stack.app.core.configuration import get_settings
from stack.app.agents.configurable_agent import get_configured_agent

logger = structlog.get_logger(__name__)
settings = get_settings()

assistant_config = {
    "configurable": {
        "type": "corrective_rag",
        # "tools": [{
        #     "name": "Retrieval",
        #     "type": "retrieval",
        #     "config": {
        #         "encoder": {
        #             "provider": "ollama",
        #             "dimensions": 384,
        #             "encoder_model": "all-minilm"
        #         },
        #         "index_name": "test",
        #         "enable_rerank": False
        #     },
        #     "multi_use": False,
        #     "description": "Look up information in uploaded files."
        # }],
        "type==corrective_rag/agent_type": "GPT 4o Mini",
        "type==corrective_rag/system_prompt": "You are a helpful assistant.",
        "type==corrective_rag/enable_web_search": True,
        "type==corrective_rag/relevance_threshold": 0.5,
        "type==corrective_rag/max_corrective_iterations": 3,
        "type==corrective_rag/question_rewriter_prompt": (
            "You are an expert at reformulating questions to be clearer and more effective for search."
        ),
        "user_id": "default",
        "thread_id": str(uuid.uuid4()),
        # "assistant_id": str(uuid.uuid4()),
        "assistant_id": "ba8b90a5-17de-48ff-8f0d-3e0c88344ee8",
    }
}

async def setup_infrastructure():
    """Initialize database and checkpointer."""
    await initialize_db()
    await initialize_checkpointer()

async def cleanup_infrastructure():
    """Cleanup database connections."""
    await cleanup_db()

async def run_agent(
    query: str,
    config_path: Optional[str] = None,
    config_dict: Optional[dict] = None
) -> None:
    """
    Run the agent with the specified configuration.
    
    Args:
        query: The query to send to the agent
        config_path: Path to a JSON configuration file
        config_dict: Configuration dictionary to use directly
    """
    try:
        # Initialize infrastructure
        await setup_infrastructure()
        
        # Prepare the message
        message = HumanMessage(content=query)
        
        # Initialize state
        initial_state = {
            "messages": [message],
            "question": query,
            "generation": "",
            "web_search_needed": False,
            "documents": [],
            "iteration_count": 0
        }

        # Load config from file if provided
        if config_path:
            with open(config_path, 'r') as f:
                config = json.load(f)
        # Use provided config dict if available
        elif config_dict:
            config = config_dict
        else:
            # Default test configuration for corrective RAG
            config = assistant_config
            # Merge the input state into the configurable section
            config["configurable"].update(initial_state)

        logger.info("Starting agent with configuration", config=config)
        
        agent = get_configured_agent()
        
        async for event in agent.astream_events(
            initial_state,
            config=config,
            version="v1"
        ):
            # Print different event types with appropriate formatting
            if event["event"] == "on_chat_model_start":
                print("\nStarting chat...\n")
            elif event["event"] == "on_chat_model_stream":
                print(event["data"]["chunk"].content, end="", flush=True)
            elif event["event"] == "on_tool_start":
                print(f"\n\nUsing tool: {event['name']}\n")
            elif event["event"] == "on_tool_end":
                print(f"\nTool result: {event['data']['output']}\n")
            elif event["event"] == "on_chain_end":
                print("\nChat completed.\n")
            else:
                print(f"\nEvent: {event}\n")

    except Exception as e:
        logger.error("Error during agent execution", error=str(e), exc_info=True)
        raise
    finally:
        # Ensure we clean up infrastructure even if there's an error
        await cleanup_infrastructure()

def main():
    # Load environment variables
    load_dotenv()
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Debug Configurable Agent')
    parser.add_argument('--query', type=str, default="Tell me about Aligning LLM-Assisted Evaluation of LLM Outputs with Human Preferences",
                      help='Query to send to the agent')
    parser.add_argument('--config', type=str,
                      help='Path to JSON configuration file')
    
    args = parser.parse_args()
    
    
    try:
        asyncio.run(run_agent(
            query=args.query,
            config_path=args.config,
            config_dict=args.config
        ))
    except KeyboardInterrupt:
        print("\nDebug session interrupted by user")
    except Exception as e:
        logger.error("Fatal error in main", error=str(e), exc_info=True)
        raise

if __name__ == "__main__":
    main()