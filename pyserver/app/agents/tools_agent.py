from typing import cast

from langchain.tools import BaseTool
from langchain_core.language_models.base import LanguageModelLike
from langchain_core.messages import (
    AIMessage,
    FunctionMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langgraph.checkpoint import BaseCheckpointSaver
from langgraph.graph import END
from langgraph.graph.message import MessageGraph
from langgraph.prebuilt import ToolExecutor, ToolInvocation

from app.schema.message_types import LiberalToolMessage


def get_tools_agent_executor(
    tools: list[BaseTool],
    llm: LanguageModelLike,
    system_message: str,
    interrupt_before_action: bool,
    checkpoint: BaseCheckpointSaver,
):
    async def _get_messages(messages):
        msgs = []
        for m in messages:
            if isinstance(m, LiberalToolMessage):
                _dict = m.dict()
                _dict["content"] = str(_dict["content"])
                m_c = ToolMessage(**_dict)
                msgs.append(m_c)
            elif isinstance(m, FunctionMessage):
                # anthropic doesn't like function messages
                msgs.append(HumanMessage(content=str(m.content)))
            else:
                msgs.append(m)

        return [SystemMessage(content=system_message)] + msgs

    llm_with_tools = llm.bind_tools(tools) if tools else llm
    
    agent = _get_messages | llm_with_tools
    tool_executor = ToolExecutor(tools)

    def should_continue(messages):
        last_message = messages[-1]
        # If there is no function call, then we finish
        if not last_message.tool_calls:
            return "end"
        # Otherwise we continue
        return "continue"

    async def call_tool(messages):
        actions: list[ToolInvocation] = []
        # Based on the continue condition
        # we know the last message involves a function call
        last_message = cast(AIMessage, messages[-1])
        for tool_call in last_message.tool_calls:
            # construct a ToolInvocation from the function_call
            actions.append(
                ToolInvocation(
                    tool=tool_call["name"],
                    tool_input=tool_call["args"],
                )
            )
        # call the tool_executor and get back a response
        responses = await tool_executor.abatch(actions)
        # use the response to create a ToolMessage
        tool_messages = [
            LiberalToolMessage(
                tool_call_id=tool_call["id"],
                name=tool_call["name"],
                content=response,
            )
            for tool_call, response in zip(last_message.tool_calls, responses)
        ]
        return tool_messages

    workflow = MessageGraph()

    workflow.add_node("agent", agent)
    workflow.add_node("action", call_tool)

    workflow.set_entry_point("agent")

    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            # If `tools`, then we call the tool node.
            "continue": "action",
            # Otherwise we finish.
            "end": END,
        },
    )

    # add a normal edge from `tools` to `agent`.
    # after `tools` is called, `agent` node is called next.
    workflow.add_edge("action", "agent")

    return workflow.compile(
        checkpointer=checkpoint,
        interrupt_before=["action"] if interrupt_before_action else None,
    )
