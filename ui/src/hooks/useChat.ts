import { TMessage } from "@/data-provider/types";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { mergeMessagesById } from "./useStream";

async function getState(threadId: string) {
  const { values, next } = await fetch(
    `${process.env.NEXT_PUBLIC_BASE_API_URL}/api/v1/threads/${threadId}/state`,
    {
      headers: {
        Accept: "application/json",
      },
    },
  ).then((r) => (r.ok ? r.json() : Promise.reject(r.statusText)));
  return { values, next };
}

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

  const refreshMessages = useCallback(async () => {
    if (threadId) {
      const { values, next } = await getState(threadId);
      const messages = values
        ? Array.isArray(values)
          ? values
          : values.messages
        : [];
      setMessages(messages);
      setNext(next);
    }
  }, [threadId]);

  useEffect(() => {
    refreshMessages();
    return () => {
      setMessages(null);
    };
  }, [threadId, refreshMessages]);

  useEffect(() => {
    async function fetchMessages() {
      if (threadId) {
        const { values, next } = await getState(threadId);
        const messages = Array.isArray(values) ? values : values.messages;
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
  }, [stream?.status]);

  return useMemo(
    () => ({
      refreshMessages,
      messages: mergeMessagesById(messages, stream?.messages),
      next,
    }),
    [messages, stream?.messages, next, refreshMessages],
  );
}
