"use client";

import { Composer } from "./components/composer";
import MessagesContainer from "./components/messages-container";
import { useStream } from "@/hooks/useStream";
import { useEffect, useState } from "react";
import { MessageType, TStreamState } from "@/data-provider/types";
import { useSlugRoutes } from "@/hooks/useSlugParams";
import { useRouter } from "next/navigation";
import { QueryClient, useQueryClient } from "@tanstack/react-query";
import { QueryKeys, useGenerateTitle } from "@/data-provider/query-service";
import { useChatMessages } from "@/hooks/useChat";

export default function ChatPanel() {
  const [userMessage, setUserMessage] = useState("");
  const [isNewThread, setIsNewThread] = useState(false);

  const queryClient = useQueryClient();

  const {
    stream,
    startStream,
    stopStream: handleStop,
    isStreaming,
  } = useStream();
  
  const generateTitle = useGenerateTitle();

  const { assistantId, threadId } = useSlugRoutes();

  const router = useRouter();

  const { messages } = useChatMessages(threadId as string, stream);

  useEffect(() => {
    const isStreamDone = stream?.status === "done";

    if (isNewThread && isStreamDone) {

      generateTitle.mutate({
        thread_id: stream?.thread_id as string,
        history: messages
      });

      router.push(`/a/${assistantId}/c/${stream?.thread_id}`);
    }
  }, [stream?.status]);

  const handleSend = async () => {
    const input = [
      {
        content: userMessage,
        type: MessageType.HUMAN,
        example: false,
      },
    ];

    setUserMessage("");

    if (!threadId) setIsNewThread(true);

    await startStream({
      input,
      thread_id: threadId as string,
      assistant_id: assistantId as string,
    });
  };

  return (
    <div className="h-full w-full gap-4 flex flex-col" data-testid="chat-panel">
      <div className="h-full flex flex-col rounded">
        {threadId || isNewThread ? (
          <MessagesContainer
            threadId={threadId as string}
            stream={stream as TStreamState}
            startStream={startStream}
          />
        ) : (
          <div className="self-center h-full items-center flex">
            <h1 className="bg-sky-100 border border-blue-400 text-blue-700 px-4 py-3 rounded relative">
              {"Select an assistant to begin a conversation."}
            </h1>
          </div>
        )}

        <Composer
          onChange={(e) => setUserMessage(e.target.value)}
          value={userMessage}
          onSend={handleSend}
          onStop={handleStop}
          isStreaming={isStreaming}
          disabled={!assistantId}
        />
      </div>
    </div>
  );
}
