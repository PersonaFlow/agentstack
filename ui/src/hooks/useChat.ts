import { TMessage, TStreamState } from "@/data-provider/types";
import { useEffect } from "react";
import { mergeMessagesById } from "./useStream";
import { useDeleteMessage, useThreadState } from "@/data-provider/query-service";
import { useAtom } from "jotai";
import { messagesAtom } from "@/store";

export function useChatMessages(
  threadId: string | null,
  stream: TStreamState | null,
) {
  const [streamedMessages, setStreamedMessages] = useAtom(messagesAtom)

  const { data: threadData, refetch, isFetched } = useThreadState(threadId as string, {
    enabled: !!threadId
  });

  const deleteMessage = useDeleteMessage()

  // Refetch messages after streaming
  useEffect(() => {
    if (stream?.status !== "inflight" && threadId) {
      refetch();
    }

    if (stream?.status === "stopped") {
      const lastHumanMsg = streamedMessages?.slice().reverse().find(message => message.type === 'human');
      console.log(lastHumanMsg);
      // deleteMessage.mutate(lastHumanMsg?.id as string)
    }
  }, [stream?.status, threadId, refetch]);

  // Stop persisting streamed messages after streaming and message refetch
  useEffect(() => {
    if (isFetched) {
      setStreamedMessages([])
    }
  },[isFetched])

  useEffect(() => {
    if (stream?.messages) {
      setStreamedMessages(stream.messages as TMessage[])
    }
  }, [stream?.messages])

  const messages = threadData?.values ? threadData.values : null;

  return {
    messages: mergeMessagesById(messages, streamedMessages),
    next: threadData?.next || [],
    refreshMessages: refetch
  };
}
