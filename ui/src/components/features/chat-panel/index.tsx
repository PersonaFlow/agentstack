"use client";

import { Composer } from "./components/composer";
import MessagesContainer from "./components/messages-container";
import { useThreadState } from "@/data-provider/query-service";
import { useToast } from "@/components/ui/use-toast";
import { useStream } from "@/hooks/useStream";
import { useState } from "react";
import { MessageType } from "@/data-provider/types";
import Spinner from "@/components/ui/spinner";
import { useSlugRoutes } from "@/hooks/useSlugParams";

export default function ChatPanel() {
  const {assistantId, threadId} = useSlugRoutes()

  const {
    data: threadState,
    isError,
    isLoading: isLoadingThreads,
  } = useThreadState(threadId as string, {
    enabled: !!assistantId
  });

  const [userMessage, setUserMessage] = useState("");
  const { stream, startStream } = useStream();
  const { toast } = useToast();

  const handleSend = async () => {
    if (!assistantId) {
      toast({
        variant: "destructive",
        title: "Please select an assistant.",
      });
      return;
    }
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

  if (!threadState && isError)
    return <div>There was an issue fetching messages.</div>;

  return (
    <div className="h-full w-full gap-4 flex flex-col">
      {isLoadingThreads && <Spinner />}
      <MessagesContainer
        threadId={threadId as string}
        // @ts-ignore
        stream={stream}
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
