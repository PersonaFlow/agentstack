"use client";
import {
  MessageType,
  TMessage,
  TStreamState,
  TToolCall,
} from "@/data-provider/types";
import { useAssistant } from "@/data-provider/query-service";
import MessageItem from "./message-item";
import { ReactNode, useEffect, useRef } from "react";
import { useChatMessages } from "@/hooks/useChat";
import ToolContainer from "../../tools/tool-container";
import { ToolResult } from "../../tools/tool-result";
import { useSlugRoutes } from "@/hooks/useSlugParams";
import { ArrowDownCircle } from "lucide-react";
import { useStream } from "@/hooks/useStream";


type Props = {
  streamingMessage?: TMessage | null;
  onRetry?: VoidFunction;
  threadId: string;
  stream: TStreamState;
  startStream: ({
    input,
    thread_id,
    assistant_id,
    user_id,
  }: TStartStreamProps) => Promise<void>;
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
  startStream,
}: Props) {
  const { messages, next } = useChatMessages(threadId, stream);
  const prevMessages = usePrevious(messages);
  const { assistantId } = useSlugRoutes();
  const { data: selectedAssistant, isLoading: isLoadingAssistant } =
    useAssistant(assistantId as string, {
      enabled: !!assistantId,
    });

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
  }, [messages, prevMessages]);

  return (
      <div className="p-6 overflow-y-scroll" ref={divRef}>
        {messages?.map((message, index) => {
          console.log("Rendering message:", message);
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
            <MessageItem 
              message={message} 
              assistant={selectedAssistant} 
              key={`${message.id}-${index}`} 
            />
          );
        })}
        {next.length > 0 && stream?.status !== "inflight" && (
          <div
            className="flex items-center rounded-md bg-blue-50 px-2 py-1 text-xs font-medium text-blue-800 ring-1 ring-inset ring-blue-600/20 cursor-pointer"
            onClick={() =>
              startStream({
                input: null,
                thread_id: threadId,
                assistant_id: assistantId as string,
              })
            }
          >
            <ArrowDownCircle className="h-5 w-5 mr-1" />
            Click to continue.
          </div>
        )}
      </div>
  );
}
