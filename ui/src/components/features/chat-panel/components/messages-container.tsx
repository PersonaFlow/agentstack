"use client";
import {
  MessageType,
  TMessage,
  TStreamState,
  TToolCall,
  TToolResult,
} from "@/data-provider/types";
import { useAssistant } from "@/data-provider/query-service";
import MessageItem from "./message-item";
import { useParams } from "next/navigation";
import { ReactNode, useEffect, useRef, useState } from "react";
import Spinner from "@/components/ui/spinner";
import { useChatMessages } from "@/hooks/useChat";
import ToolContainer from "../../tools/tool-container";
import { ToolResult } from "../../tools/tool-result";
import { useSlugRoutes } from "@/hooks/useSlugParams";


type Props = {
  streamingMessage?: TMessage | null;
  onRetry?: VoidFunction;
  threadId: string;
  stream: TStreamState;
};

function usePrevious<T>(value: T): T | undefined {
  const ref = useRef<T>();
  useEffect(() => {
    ref.current = value;
  });
  return ref.current;
}

export default function MessagesContainer({
  streamingMessage,
  onRetry,
  threadId,
  stream
}: Props) {
  const { messages } = useChatMessages(threadId, stream);
  const prevMessages = usePrevious(messages);
  const {assistantId} = useSlugRoutes();

  const {data: selectedAssistant, isLoading: isLoadingAssistant} = useAssistant(assistantId as string, {
    enabled: !!assistantId
  })


  const divRef = useRef<HTMLDivElement>(null);

  // Auto-scroll
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
            <MessageItem message={message} assistant={selectedAssistant} key={`${message.id}-${index}`} />
          );
        })}
      </div>
  );
}
