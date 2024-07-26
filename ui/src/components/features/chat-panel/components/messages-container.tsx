"use client";
import {
  MessageType,
  TMessage,
  TToolCall,
  TToolResult,
} from "@/data-provider/types";
import MessageItem from "./message-item";
import { useParams } from "next/navigation";
import { ReactNode, useEffect, useRef, useState } from "react";
import Spinner from "@/components/ui/spinner";
import { useChatMessages } from "@/hooks/useChat";
import ToolContainer from "../../tools/tool-container";
import { ToolResult } from "../../tools/tool-result";

type Props = {
  isStreaming?: boolean;
  stream?: TMessage[];
  streamingMessage?: TMessage | null;
  onRetry?: VoidFunction;
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
  conversationId,
  threadId,
}: Props) {
  const { messages, next, refreshMessages } = useChatMessages(threadId, stream);
  const prevMessages = usePrevious(messages);
  const divRef = useRef<HTMLDivElement>(null);

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
        {messages?.map((message, index) => {
          const isToolCall =
            message.tool_calls?.length && message.tool_calls.length > 0;

          const isToolResult = message.type === MessageType.TOOL;

          if (isToolResult) {
            return (
              <ToolResult toolResult={message} key={`${message.id}-${index}`} />
            );
          }

          if (isToolCall) {
            return (
              <ToolContainer
                toolCalls={message.tool_calls as TToolCall[]}
                key={`${message.id}-${index}`}
              />
            );
          }

          return (
            <MessageItem message={message} key={`${message.id}-${index}`} />
          );
        })}
      </div>
    </div>
  );
}
