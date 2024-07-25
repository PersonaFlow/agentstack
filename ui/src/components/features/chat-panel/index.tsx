"use client";

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
import Spinner from "@/components/ui/spinner";

export default function ChatPanel() {
  const [conversation, setConversation] = useAtom(conversationAtom);
  const [assistant] = useAtom(assistantAtom);
  const { id: threadId } = useParams<{ id: string }>();
  const {
    data: threadState,
    isError,
    isLoading: isLoadingThreads,
  } = useThreadState(threadId);
  const [userMessage, setUserMessage] = useState("");
  const { stream, startStream } = useStream();
  const { toast } = useToast();

  const handleSend = async () => {
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
        type: MessageType.HUMAN,
        example: false,
      },
    ];

    setUserMessage("");

    await startStream({
      input,
      thread_id: threadId,
      assistant_id: assistant.id as string,
    });
  };

  if (!threadState && isError)
    return <div>There was an issue fetching messages.</div>;

  return (
    <div className="h-full w-full gap-4 flex flex-col">
      {isLoadingThreads && <Spinner />}
      <MessagesContainer
        threadId={threadId}
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
