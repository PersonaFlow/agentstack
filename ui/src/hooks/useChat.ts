import { TMessage, TStreamState, TStreamStatus } from "@/data-provider/types";
import { useEffect, useMemo, useRef } from "react";
import { mergeMessagesById } from "./useStream";
import { useThreadState } from "@/data-provider/query-service";
import { useAtom, useSetAtom } from "jotai";
import { mergedMessagesAtom, messagesAtom } from "@/store";
import { useStream } from "./stream";

function usePrevious<T>(value: T): T | undefined {
  const ref = useRef<T>();
  useEffect(() => {
    ref.current = value;
  });
  return ref.current;
}

export function useChatMessages(
  threadId: string | undefined,
  // stream: TStreamState | null,
) {
  const [streamedMessages, setStreamedMessages] = useAtom(messagesAtom);
  const setMergedMessages = useSetAtom(mergedMessagesAtom);
  const stream = useStream();
  const prevStreamStatus = usePrevious(stream?.status);

  const {
    data: threadStateData,
    refetch,
    isFetched,
  } = useThreadState(threadId as string, {
    enabled: !!threadId,
  });

  // Only refetch when transitioning from inflight to non-inflight
  useEffect(() => {
    if (
      prevStreamStatus === TStreamStatus.INFLIGHT &&
      stream?.status !== TStreamStatus.INFLIGHT &&
      threadId
    ) {
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

  const threadStateMessages = threadStateData?.values
    ? threadStateData.values
    : null;
  const next = threadStateData?.next || [];
  const mergedMessages = useMemo(
    () => mergeMessagesById(threadStateMessages, streamedMessages),
    [threadStateMessages, streamedMessages],
  );

  useEffect(() => {
    setMergedMessages(mergedMessages);
  }, [mergedMessages]);

  return {
    messages: mergedMessages,
    next,
    refreshMessages: refetch,
  };
}
