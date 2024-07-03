"use client";
import { TMessage } from "@/data-provider/types";
import MessageItem from "./message-item";
import { useParams } from "next/navigation";
import { ReactNode, useEffect, useRef } from "react";
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

function usePrevious<T>(value: T): T | undefined {
  const ref = useRef<T>();
  useEffect(() => {
    ref.current = value;
  });
  return ref.current;
}

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
  const prevMessages = usePrevious(messages);
  const divRef = useRef(null);

  useEffect(() => {
    if (divRef.current) {
      divRef.current.scrollTo({
        top: divRef.current.scrollHeight,
        behavior:
          prevMessages && prevMessages?.length === messages?.length
            ? "smooth"
            : undefined,
      });
    }
  }, [messages]);

  return (
    <div className="h-full flex flex-col">
      <div className="p-6 overflow-y-scroll" ref={divRef}>
        {messages?.map((message) => (
          <MessageItem message={message} key={message.id} />
        ))}
      </div>
      {composer}
    </div>
  );
}
