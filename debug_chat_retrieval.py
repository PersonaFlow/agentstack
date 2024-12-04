#!/usr/bin/env python3
"""
Debug script for testing the ConfigurableRetrieval architecture.
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

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from stack.app.core.datastore import initialize_checkpointer, initialize_db, cleanup_db
from stack.app.core.configuration import get_settings
from stack.app.agents.configurable_agent import get_configured_agent

logger = structlog.get_logger(__name__)
settings = get_settings()

# Default test configuration for chat retrieval
DEFAULT_AGENT_CONFIG = {
    "configurable": {
        "type": "chat_retrieval",
        "llm_type": "GPT 4o Mini",
        "system_message": "You are a helpful assistant.",
        "retrieval_description": "Can be used to look up information that was uploaded to this assistant.",
        "user_id": "default",
        "thread_id": str(uuid.uuid4()),
        "assistant_id": "2cb8752f-1b2b-4400-8b7a-7dd195f420d6",
        "retrieval_config": {
            "index_name": "test",  
            "encoder": {
                "provider": "ollama",
                "encoder_model": "all-minilm",
                "dimensions": 384
            },
            "enable_rerank": False
        }
    }
}

async def setup_infrastructure():
    """Initialize database and checkpointer."""
    await initialize_db()
    await initialize_checkpointer()

async def cleanup_infrastructure():
    """Cleanup database connections."""
    await cleanup_db()

async def run_agent(query: str) -> None:
    """
    Run the agent with the specified configuration.
    
    Args:
        query: The query to send to the agent
    """
    try:
        # Initialize infrastructure
        await setup_infrastructure()
        
        # Prepare the message and initial state
        message = HumanMessage(content=query)
        initial_state = {
            "messages": [message],
            "msg_count": 0
        }
        
        config = DEFAULT_AGENT_CONFIG.copy()


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
    parser = argparse.ArgumentParser(description='Debug Chat Retrieval Agent')
    parser.add_argument('--query', type=str, 
                       default="Tell me about Aligning LLM-Assisted Evaluation of LLM Outputs with Human Preferences",
                       help='Query to send to the agent')
    
    args = parser.parse_args()
    
    try:
        asyncio.run(run_agent(query=args.query))
    except KeyboardInterrupt:
        print("\nDebug session interrupted by user")
    except Exception as e:
        logger.error("Fatal error in main", error=str(e), exc_info=True)
        raise

if __name__ == "__main__":
    main()