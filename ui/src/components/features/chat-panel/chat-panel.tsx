"use client";

import { Composer } from "./components/composer";
import MessagesContainer from "./components/messages-container";
import { useToast } from "@/components/ui/use-toast";
import { useStream } from "@/hooks/useStream";
import { useState } from "react";
import { MessageType, TStreamState } from "@/data-provider/types";
import { useSlugRoutes } from "@/hooks/useSlugParams";

export default function ChatPanel() {
  const [userMessage, setUserMessage] = useState("");
  const { stream, startStream } = useStream();
  
  const { assistantId, threadId } = useSlugRoutes();

  const handleSend = async () => {
    const input = [
      {
        content: userMessage,
        type: MessageType.HUMAN,
        example: false,
      },
    ];

    setUserMessage("");

    await startStream({
      input,
      thread_id: threadId as string,
      assistant_id: assistantId as string,
    });
  };

  return (
    <div className="h-full w-full gap-4 flex flex-col">
      <div className="h-full flex flex-col">
        
        {threadId ? (
          <MessagesContainer
            threadId={threadId as string}
            stream={stream as TStreamState}
          />
        ) : (
          <h1>Welcome!</h1>
        )}

        <Composer
          onChange={(e) => setUserMessage(e.target.value)}
          value={userMessage}
          sendMessage={handleSend}
          disabled={!assistantId}
        />
      </div>
    </div>
  );
}
