"use client";

import { useChat } from "@/hooks/useChat";
import { Composer } from "./components/composer";
import MessagesContainer from "./components/messages-container";

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

export default function ChatPanel() {
  const { setUserMessage, userMessage, handleSend: send } = useChat();
  const {data: messages} = 

  const handleSend = () => {
    send();
  };

  return (
    <div className="h-full w-full gap-4 flex flex-col">
      <MessagesContainer
        messages={data}
        composer={
          <Composer
            onChange={(e) => setUserMessage(e.target.value)}
            value={userMessage}
            sendMessage={handleSend}
          />
        }
      />
    </div>
  );
}
