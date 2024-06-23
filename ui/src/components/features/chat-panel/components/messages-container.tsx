"use client";
import { TMessage, TMessageState } from "@/data-provider/types";
import MessageItem from "./message-item";
import { useParams } from "next/navigation";
import { ReactNode } from "react";

type Props = {
  isStreaming?: boolean;
  messages: TMessageState;
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
  const { values } = messages;
  //   const {data: messages} = useMessagesByThread(threadId)

  return (
    <div className="h-full flex flex-col">
      <div className="p-6">
        {values.map((message) => (
          <MessageItem message={message} key={message.id} />
        ))}
        {streamingMessage && <MessageItem message={streamingMessage} />}
      </div>
      {composer}
    </div>
  );
}
