import { TMessage } from "@/data-provider/types";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { mergeMessagesById } from "./useStream";
import { useThreadState } from "@/data-provider/query-service";

// async function getState(threadId: string) {
//   const { values, next } = await fetch(
//     `${process.env.NEXT_PUBLIC_BASE_API_URL}/api/v1/threads/${threadId}/state`,
//     {
//       headers: {
//         Accept: "application/json",
//       },
//     },
//   ).then((r) => (r.ok ? r.json() : Promise.reject(r.statusText)));
//   return { values, next };
// }

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
) {
  const [messages, setMessages] = useState<TMessage[] | null>(null);
  const [next, setNext] = useState<string[]>([]);
  const prevStreamStatus = usePrevious(stream?.status);

  const { data: threadData } = useThreadState(threadId);

  const refreshMessages = useCallback(async () => {
    if (threadId && threadData) {
      const { values, next } = threadData;
      const messages = values
        ? Array.isArray(values)
          ? values
          : values.messages
        : [];
      setMessages(messages);
      setNext(next);
    }
  }, [threadId, threadData]);

  useEffect(() => {
    refreshMessages();
    return () => {
      setMessages(null);
    };
  }, [threadId, refreshMessages]);

  useEffect(() => {
    async function fetchMessages() {
      if (threadId && threadData) {
        const { values: messages, next } = threadData;
        setMessages(messages);
        setNext(next);
        stopStream?.(true);
      }
    }

    if (prevStreamStatus === "inflight" && stream?.status !== "inflight") {
      setNext([]);
      fetchMessages();
    }

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [stream?.status, threadData]);

  return useMemo(
    () => ({
      refreshMessages,
      messages: mergeMessagesById(messages, stream?.messages),
      next,
    }),
    [messages, stream?.messages, next, refreshMessages],
  );
}
