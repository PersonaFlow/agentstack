"use client";
import { useAssistant } from "@/data-provider/query-service";
import {
  MessageType,
  TAssistant,
  TMessage,
  TToolCall,
} from "@/data-provider/types";
import { useStream } from "@/hooks/stream";
import { useChatMessages } from "@/hooks/useChat";
import { useSlugRoutes } from "@/hooks/useSlugParams";
import { TStartStreamFn } from "@/hooks/useStream";
import { ArrowDownCircle } from "lucide-react";
import { forwardRef, useEffect, useRef, useState } from "react";
import ToolContainer from "../../tools/tool-container";
import { ToolResult } from "../../tools/tool-result";
import { AssistantMessage, HumanMessage } from "./message-item";

type Props = {
  streamingMessage?: TMessage | null;
  onRetry?: VoidFunction;
  threadId: string | undefined;
  // stream: TStreamState;
  startStream: TStartStreamFn;
};

function usePrevious<T>(value: T): T | undefined {
  const ref = useRef<T>();
  useEffect(() => {
    ref.current = value;
  });
  return ref.current;
}

export default function MessagesContainer({
  // streamingMessage,
  // onRetry,
  threadId,
  // stream,
  startStream,
}: Props) {
  const stream = useStream();
  // const startStream = useStartStream();
  const { messages, next } = useChatMessages(threadId);
  const prevMessagesLength = usePrevious(messages.length);
  const { assistantId } = useSlugRoutes();
  const { data: selectedAssistant, isLoading: isLoadingAssistant } =
    useAssistant(assistantId as string, {
      enabled: !!assistantId,
    });
  const [error, setError] = useState<boolean>(false);
  const divRef = useRef<HTMLDivElement>(null);

  // Auto-scroll
  useEffect(() => {
    console.log("messages.length", messages.length, prevMessagesLength);
    if (
      divRef.current &&
      prevMessagesLength &&
      prevMessagesLength === messages?.length
    ) {
      console.log("Scrolling to bottom", divRef.current.scrollHeight);
      divRef.current.scrollTo({
        top: divRef.current.scrollHeight - divRef.current.clientHeight,
        behavior: "smooth",
      });
    }
  }, [messages.length, prevMessagesLength]);

  // useEffect(() => {
  //   new ResizeObserver((entry, observer) => {
  //     console.log("Transition ended", entry);
  //   }).observe(divRef.current as Element);
  //   return () => {};
  // }, [divRef.current]);

  if (isLoadingAssistant) {
    return <div>Loading...</div>;
  }
  if (!selectedAssistant) {
    return <div>Assistant not found</div>;
  }

  return (
    <div className="p-6 overflow-y-scroll" ref={divRef}>
      {messages?.map((message) => (
        <Message
          key={`chat-message-${message.id}`}
          message={message}
          assisstant={selectedAssistant}
        />
      ))}

      {error && (
        <div className="text-red-500">
          There has been some error with current stream.
        </div>
      )}

      {next.length > 0 && stream?.status == "done" && (
        <div
          className="flex items-center rounded-md bg-blue-50 px-2 py-1 text-xs font-medium text-blue-800 ring-1 ring-inset ring-blue-600/20 cursor-pointer"
          onClick={() =>
            startStream({
              input: null,
              thread_id: threadId as string,
              assistant_id: assistantId as string,
              options: {
                onError: () => {
                  console.log("Error");
                  setError(true);
                },
              },
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

const Message = ({
  message,
  assisstant,
}: {
  message: TMessage;
  assisstant: TAssistant;
}) => {
  if (isToolResult(message)) {
    return <ToolResult toolResult={message} />;
  }

  if (isToolCall(message)) {
    return <ToolContainer toolCalls={message.tool_calls as TToolCall[]} />;
  }

  if (isHumanMessage(message)) {
    return <HumanMessage messageText={message.content as string} ref={ref} />;
  }

  if (isAssisstantMessage(message)) {
    return (
      <AssistantMessage
        assisstant={assisstant}
        messageText={message.content as string}
      />
    );
  }

  return null;
};

function isAssisstantMessage(message: TMessage) {
  return message.type === MessageType.AI;
}

function isHumanMessage(message: TMessage) {
  return message.type === MessageType.HUMAN;
}

function isToolResult(message: TMessage) {
  return message.type === MessageType.TOOL;
}

function isToolCall(message: TMessage) {
  return message.tool_calls?.length && message.tool_calls.length > 0;
}
