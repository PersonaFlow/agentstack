import { TMessage, TStreamState } from "@/data-provider/types";
import { useEffect, useRef } from "react";
import { mergeMessagesById } from "./useStream";
import { useThreadState } from "@/data-provider/query-service";
import { useAtom } from "jotai";
import { messagesAtom } from "@/store";

function usePrevious<T>(value: T): T | undefined {
  const ref = useRef<T>();
  useEffect(() => {
    ref.current = value;
  });
  return ref.current;
}

export function useChatMessages(
  threadId: string | null,
  stream: TStreamState | null,
) {
  const [streamedMessages, setStreamedMessages] = useAtom(messagesAtom);
  const prevStreamStatus = usePrevious(stream?.status);
  
  const { data: threadData, refetch, isFetched } = useThreadState(threadId as string, {
    enabled: !!threadId
  });

  // Only refetch when transitioning from inflight to non-inflight
  useEffect(() => {
    if (prevStreamStatus === "inflight" && 
        stream?.status !== "inflight" && 
        threadId) {
      refetch();
    }
  }, [stream?.status, threadId, refetch, prevStreamStatus]);

  // Clear streamed messages after fetching thread state
  useEffect(() => {
    if (isFetched) {
      setStreamedMessages([]);
    }
  }, [isFetched, setStreamedMessages]);

  // Update streamed messages during streaming
  useEffect(() => {
    if (stream?.messages) {
      setStreamedMessages(stream.messages as TMessage[]);
    }
  }, [stream?.messages, setStreamedMessages]);

  const messages = threadData?.values ? threadData.values : null;
  const next = threadData?.next || [];

  return {
    messages: mergeMessagesById(messages, streamedMessages),
    next,
    refreshMessages: refetch
  };
}

