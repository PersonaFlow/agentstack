"use client";
import MessageItem from "./message-item";
import { useParams } from "next/navigation";

const data = {
  values: [
    {
      content: "hello",
      additional_kwargs: {},
      response_metadata: {},
      type: "human",
      name: null,
      id: "human-0.98618096892379",
      example: false,
    },
    {
      content: "Hello! How can I assist you today?",
      additional_kwargs: {},
      response_metadata: {
        finish_reason: "stop",
      },
      type: "ai",
      name: null,
      id: "run-8ad1bd14-6340-4afw9-b357-32awc210f150f",
      example: false,
      tool_calls: [],
      invalid_tool_calls: [],
    },
    {
      content: "I am working on a project called PersonaFlow.",
      additional_kwargs: {},
      response_metadata: {},
      type: "human",
      name: null,
      id: "human-0.9861809w968792379",
      example: false,
    },
    {
      content: "That's neat! How can I help?",
      additional_kwargs: {},
      response_metadata: {
        finish_reason: "stop",
      },
      type: "ai",
      name: null,
      id: "run-8ad1bd14-6340-4af9-b357-32wac210f150f",
      example: false,
      tool_calls: [],
      invalid_tool_calls: [],
    },
    {
      content: "Help me understand the meaning of life.",
      additional_kwargs: {},
      response_metadata: {},
      type: "human",
      name: null,
      id: "human-0.986109968792379",
      example: false,
    },
  ],
  next: [],
};

export default function Messages() {
  const { values: messages } = data;
  const { id: threadId } = useParams();

  //   const {data: messages} = useMessagesByThread(threadId)

  return (
    <div className="p-6">
      {messages.map((message) => (
        <MessageItem message={message} key={message.id} />
      ))}
    </div>
  );
}
