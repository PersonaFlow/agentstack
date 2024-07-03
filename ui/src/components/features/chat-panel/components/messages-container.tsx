"use client";
import { TMessage } from "@/data-provider/types";
import MessageItem from "./message-item";
import { useParams } from "next/navigation";
import { ReactNode } from "react";
import Spinner from "@/components/ui/spinner";
import { useChatMessages } from "@/hooks/useChat";

type Props = {
  isStreaming?: boolean;
  stream?: TMessage[];
  streamingMessage?: TMessage | null;
  onRetry?: VoidFunction;
  composer: ReactNode;
  conversationId?: string;
  threadId: string;
};

export default function MessagesContainer({
  isStreaming,
  stream,
  streamingMessage,
  onRetry,
  composer,
  conversationId,
  threadId,
}: Props) {
  const { messages, next, refreshMessages } = useChatMessages(threadId, stream);
  return (
    <div className="h-full flex flex-col">
      <div className="p-6 overflow-y-scroll">
        {messages?.map((message) => (
          <MessageItem message={message} key={message.id} />
        ))}
      </div>
      {composer}
    </div>
  );
}
