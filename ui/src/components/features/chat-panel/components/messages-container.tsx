"use client";
import {
  MessageType,
  TMessage,
  TStreamState,
  TToolCall,
} from "@/data-provider/types";
import MessageItem from "./message-item";
import { useEffect, useRef } from "react";
import { useChatMessages } from "@/hooks/useChat";
import ToolContainer from "../../tools/tool-container";
import { ToolResult } from "../../tools/tool-result";
import { Button } from "@/components/ui/button";

type Props = {
  streamingMessage?: TMessage | null;
  onRetry: (message: TMessage) => void;
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
  stream,
}: Props) {
  const { messages } = useChatMessages(threadId, stream);
  const prevMessages = usePrevious(messages);

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

        const isLastMessage = index === messages.length - 1;
        const isStopped = stream?.status === "stopped";

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
          <>
            <MessageItem message={message} key={`${message.id}-${index}`} />
            {isStopped && isLastMessage && (
              <Button onClick={() => onRetry(message)}>Retry</Button>
            )}
          </>
        );
      })}
    </div>
  );
}
