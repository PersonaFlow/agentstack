#!/usr/bin/env python3
"""
Debug script for testing the configurable agent.
"""

import os
import sys
import asyncio
import json
import argparse
from typing import Optional
import structlog
from dotenv import load_dotenv, find_dotenv

# Ensure proper path resolution
try:
    # Get the absolute path of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Get the project root (parent of stack directory)
    project_root = os.path.abspath(os.path.join(script_dir))
    
    # Add project root to Python path if not already there
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        
    # Also ensure the stack directory itself is in the path
    stack_dir = os.path.join(project_root, 'stack')
    if stack_dir not in sys.path:
        sys.path.insert(0, stack_dir)
        
except Exception as e:
    print(f"Error setting up paths: {e}")
    print(f"Current sys.path: {sys.path}")
    raise

# Now we can safely import our modules
from stack.app.agents.configurable_agent import get_configured_agent
from langchain.schema.messages import HumanMessage

logger = structlog.get_logger(__name__)

def setup_environment():
    """Setup environment variables and logging"""
    # Try to load .env file from several possible locations
    env_locations = [
        os.path.join(project_root, '.env'),
        os.path.join(project_root, '..', '.env'),
        find_dotenv()
    ]
    
    for env_file in env_locations:
        if os.path.exists(env_file):
            load_dotenv(env_file)
            logger.info(f"Loaded environment from {env_file}")
            break
    
    # Log important environment variables (excluding sensitive ones)
    logger.info("Environment setup complete", 
                python_path=sys.path,
                cwd=os.getcwd())

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
        # Load config from file if provided
        if config_path:
            config_path = os.path.abspath(config_path)
            if not os.path.exists(config_path):
                raise FileNotFoundError(f"Config file not found: {config_path}")
            with open(config_path, 'r') as f:
                config = json.load(f)
        # Use provided config dict if available
        elif config_dict:
            config = config_dict
        else:
            # Default test configuration for corrective RAG
            config = {
                "configurable": {
                    "type": "corrective_rag",
                    "type==corrective_rag/agent_type": "GPT 4o Mini",
                    "type==corrective_rag/system_prompt": "You are a helpful assistant.",
                    "type==corrective_rag/enable_web_search": True,
                    "type==corrective_rag/relevance_threshold": 0.7,
                    "type==corrective_rag/interrupt_before_action": False,
                    "user_id": os.getenv("DEFAULT_USER_ID", "default"),
                    "thread_id": os.getenv("TEST_THREAD_ID", "test-thread"),
                    "assistant_id": os.getenv("TEST_ASSISTANT_ID", "test-assistant")
                }
            }

        logger.info("Starting agent with configuration", config=config)
        
        agent = get_configured_agent()
        
        async for event in agent.astream_events(
            HumanMessage(content=query),
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
        logger.error("Error during agent execution", 
                    error=str(e), 
                    error_type=type(e).__name__,
                    exc_info=True)
        raise

def main():
    # Setup environment first
    setup_environment()
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Debug Configurable Agent')
    parser.add_argument('--query', type=str, default="Tell me about machine learning",
                      help='Query to send to the agent')
    parser.add_argument('--config', type=str,
                      help='Path to JSON configuration file')
    
    args = parser.parse_args()
    
    # Example corrective RAG configuration for reference
    example_config = {
        "configurable": {
            "type": "corrective_rag",
            "type==corrective_rag/agent_type": "GPT 4o Mini",
            "type==corrective_rag/system_prompt": "You are a helpful assistant.",
            "type==corrective_rag/enable_web_search": True,
            "type==corrective_rag/relevance_threshold": 0.7,
            "type==corrective_rag/interrupt_before_action": False,
            "user_id": "default",
            "thread_id": "d04c3678-c629-4c28-b4e1-5ad6eefe99dc",
            "assistant_id": "ba8b90a5-17de-48ff-8f0d-3e0c88344ee8"
        }
    }
    
    try:
        asyncio.run(run_agent(
            query=args.query,
            config_path=args.config,
            config_dict=example_config if not args.config else None
        ))
    except KeyboardInterrupt:
        print("\nDebug session interrupted by user")
    except Exception as e:
        logger.error("Fatal error in main", error=str(e), exc_info=True)
        raise

if __name__ == "__main__":
    main()