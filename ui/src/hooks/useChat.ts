import { useStreamChat } from "@/data-provider/query-service";
import { MessageType } from "@/data-provider/types";
import { assistantAtom, conversationAtom } from "@/store";
import { useAtom } from "jotai";
import { useState } from "react";

export const useChat = (threadId: string) => {
  const [userMessage, setUserMessage] = useState("");
  const [conversation, setConversation] = useAtom(conversationAtom);
  const [assistant, setAssistant] = useAtom(assistantAtom);
  const stream = useStreamChat();

  const handleSend = () => {
    if (!conversation) return null;

    setConversation((prevConversation) => [...prevConversation, userMessage]);
    console.log(assistant?.id);
    const payload = {
      user_id: "1234",
      thread_id: threadId,
      assistant_id: assistant.id,
      input: [
        {
          content: userMessage,
          role: MessageType.HUMAN,
          example: false,
        },
      ],
    };

    stream.mutate(payload, {
      onSuccess: (res) => console.log(res),
    });
  };

  return {
    handleSend,
    userMessage,
    setUserMessage,
  };
};
