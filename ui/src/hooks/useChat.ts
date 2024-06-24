import { useStreamChat } from "@/data-provider/query-service";
import { conversationAtom } from "@/store";
import { useAtom } from "jotai";
import { useState } from "react";

export const useChat = () => {
  const [userMessage, setUserMessage] = useState("");
  const [conversation, setConversation] = useAtom(conversationAtom);
  const stream = useStreamChat();

  const handleSend = () => {
    if (!conversation) return null;
    setConversation((prevConversation) => [...prevConversation, userMessage]);
  };

  return {
    handleSend,
    userMessage,
    setUserMessage,
  };
};
