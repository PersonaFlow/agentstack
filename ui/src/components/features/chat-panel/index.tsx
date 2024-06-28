"use client";

import { useChat } from "@/hooks/useChat";
import { Composer } from "./components/composer";
import MessagesContainer from "./components/messages-container";
import { useThreadState } from "@/data-provider/query-service";
import { useAtom } from "jotai";
import { assistantAtom, conversationAtom } from "@/store";
import { useParams } from "next/navigation";
import { useToast } from "@/components/ui/use-toast";
import { useStream } from "@/hooks/useStream";
import { useState } from "react";
import { MessageType } from "@/data-provider/types";

export default function ChatPanel() {
  const [conversation, setConversation] = useAtom(conversationAtom);
  const [assistant] = useAtom(assistantAtom);
  const { id: threadId } = useParams();
  const { data: threadState } = useThreadState(threadId);
  const [userMessage, setUserMessage] = useState("");
  // const { setUserMessage, userMessage, handleSend: send } = useChat(threadId);
  const { stream, startStream } = useStream();
  const { toast } = useToast();

  const handleSend = () => {
    if (!assistant) {
      toast({
        variant: "destructive",
        title: "Please select an assistant.",
      });
      return;
    }
    const input = [
      {
        content: userMessage,
        role: MessageType.HUMAN,
        example: false,
      },
    ];
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

    startStream(input, "1234", threadId, assistant.id);
  };

  if (!threadState) return <div>There was an issue fetching messages.</div>;

  return (
    <div className="h-full w-full gap-4 flex flex-col">
      <MessagesContainer
        messages={threadState?.values.length >= 0 ? threadState?.values : []}
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
