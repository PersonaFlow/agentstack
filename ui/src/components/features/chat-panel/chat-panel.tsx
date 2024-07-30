"use client";

import { Composer } from "./components/composer";
import MessagesContainer from "./components/messages-container";
import { useStream } from "@/hooks/useStream";
import { useEffect, useState } from "react";
import { MessageType, TStreamState } from "@/data-provider/types";
import { useSlugRoutes } from "@/hooks/useSlugParams";
import { useRouter } from "next/navigation";

export default function ChatPanel() {
  const [userMessage, setUserMessage] = useState("");
  const [isNewThread, setIsNewThread] = useState(false);

  const { stream, startStream, stopStream: handleStop, isStreaming } = useStream();
  
  const { assistantId, threadId } = useSlugRoutes();

  const router = useRouter();

  useEffect(() => {
    const isStreamDone = stream?.status === 'done';

    if (isNewThread && isStreamDone && (threadId !== stream.thread_id)) {
      router.push(`/a/${assistantId}/c/${stream?.thread_id}`);
    }

  }, [stream?.status])
  
  // useEffect(() => {
  //   if (threadId && !isNewThread) {
  //     setIsNewThread(false)
  //   }
  // },[threadId])

  const handleSend = async () => {
    const input = [
      {
        content: userMessage,
        type: MessageType.HUMAN,
        example: false,
      },
    ];

    setUserMessage("");

    if (!threadId) setIsNewThread(true)
    
    await startStream({
      input,
      thread_id: threadId as string,
      assistant_id: assistantId as string,
      setIsNewThread
    });

  };

  return (
    <div className="h-full w-full gap-4 flex flex-col">
      <div className="h-full flex flex-col">
        
        {threadId || (isNewThread) ? (
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
          onSend={handleSend}
          onStop={handleStop}
          isStreaming={isStreaming}
          disabled={!assistantId}
        />
      </div>
    </div>
  );
}
