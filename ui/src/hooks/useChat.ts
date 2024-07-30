import { TMessage } from "@/data-provider/types";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { mergeMessagesById } from "./useStream";
import { useThreadState } from "@/data-provider/query-service";

function usePrevious<T>(value: T): T | undefined {
  const ref = useRef<T>();
  useEffect(() => {
    ref.current = value;
  });
  return ref.current;
}

export function useChatMessages(
  threadId: string | null,
  stream: any | null,
  stopStream?: (clear?: boolean) => void,
  isNewThread?: boolean
) {
  const { data: threadData, refetch } = useThreadState(threadId as string);

  useEffect(() => {
    if (stream?.status !== "inflight" && threadId) {
      stopStream?.(true);
      refetch();
    }
  }, [stream?.status, threadId, refetch, stopStream]);

  const messages = threadData?.values ? threadData.values : null;

  return {
    messages: mergeMessagesById(messages, stream?.messages),
    next: threadData?.next || [],
    refreshMessages: refetch
  };
  // const [messages, setMessages] = useState<TMessage[] | null>(null);
  // const [next, setNext] = useState<string[]>([]);
  
  // const { data: threadData, refetch } = useThreadState(threadId as string, {
  //   enabled: !!threadId
  // });

  // const refreshMessages = () => {
  //   if (threadId) {
  //     refetch();
  //   }
  // };

  // useEffect(() => {
  //   if (threadData) {
  //     const { values, next } = threadData;
  //     const newMessages = Array.isArray(values) ? values : values?.messages || [];
  //     setMessages(newMessages);
  //     setNext(next);
  //   }
  // }, [threadData]);

  // useEffect(() => {
  //   if (stream?.status !== "inflight" && threadData) {
  //     setNext([]);
  //     stopStream?.(true);
  //     refreshMessages();
  //   }
  // }, [stream?.status, threadData, stopStream, refetch, threadId]);

  // return {
  //   messages: mergeMessagesById(messages, stream?.messages),
  //   next,
  //   refreshMessages
  // };
  // const [messages, setMessages] = useState<TMessage[] | null>(null);
  // const [next, setNext] = useState<string[]>([]);
  // const prevStreamStatus = usePrevious(stream?.status);

  // const { data: threadData } = useThreadState(threadId as string, {
  //   enabled: !isNewThread
  // });

  // const refreshMessages = useCallback(async () => {
  //   if (threadId && threadData) {
  //     const { values, next } = threadData;
  //     const messages = values
  //       ? Array.isArray(values)
  //         ? values
  //         // @ts-ignore
  //         : values.messages
  //       : [];
  //     setMessages(messages);
  //     setNext(next);
  //   }
  // }, [threadId, threadData]);

  // useEffect(() => {
  //   refreshMessages();
  //   return () => {
  //     setMessages(null);
  //   };
  // }, [threadId, refreshMessages]);

  // useEffect(() => {
  //   async function fetchMessages() {
  //     if (threadId && threadData) {
  //       const { values: messages, next } = threadData;
  //       setMessages(messages);
  //       setNext(next);
  //       stopStream?.(true);
  //     }
  //   }

  //   if (prevStreamStatus === "inflight" && stream?.status !== "inflight") {
  //     setNext([]);
  //     fetchMessages();
  //   }

  //   // eslint-disable-next-line react-hooks/exhaustive-deps
  // }, [stream?.status, threadData]);

  // return useMemo(
  //   () => ({
  //     refreshMessages,
  //     messages: mergeMessagesById(messages, stream?.messages),
  //     next,
  //   }),
  //   [messages, stream?.messages, next, refreshMessages],
  // );
}
