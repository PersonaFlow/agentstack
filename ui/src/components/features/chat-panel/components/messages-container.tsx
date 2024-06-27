"use client";
import { TMessage } from "@/data-provider/types";
import MessageItem from "./message-item";
import { useParams } from "next/navigation";
import { ReactNode } from "react";
import Spinner from "@/components/ui/spinner";

type Props = {
  isStreaming?: boolean;
  messages?: TMessage[];
  streamingMessage?: TMessage | null;
  onRetry?: VoidFunction;
  composer: ReactNode;
  conversationId?: string;
};

export default function MessagesContainer({
  isStreaming,
  messages,
  streamingMessage,
  onRetry,
  composer,
  conversationId,
}: Props) {
  return (
    <div className="h-full flex flex-col">
      <div className="p-6">
        {messages?.map((message) => (
          <MessageItem message={message} key={message.id} />
        ))}
        {streamingMessage && <MessageItem message={streamingMessage} />}
      </div>
      {composer}
    </div>
  );
}
