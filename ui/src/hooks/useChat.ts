import { TMessage, TStreamState } from "@/data-provider/types";
import { useEffect } from "react";
import { mergeMessagesById } from "./useStream";
import { useThreadState } from "@/data-provider/query-service";
import { useAtom } from "jotai";
import { messagesAtom } from "@/store";

export function useChatMessages(
  threadId: string | null,
  stream: TStreamState | null,
) {
  // const [streamedMessages, setStreamedMessages] = useAtom(messagesAtom)

  const { data: threadData, refetch, isFetched } = useThreadState(threadId as string, {
    enabled: !!threadId
  });

  // Refetch messages after streaming ends or is aborted
  useEffect(() => {
    if (stream?.status !== "inflight" && threadId) {
      refetch();
    }
  }, [stream?.status, threadId, refetch]);

  // // Clear streamed messages after fetching thread state
  // useEffect(() => {
  //   if (isFetched) {
  //     setStreamedMessages([]);
  //   }
  // }, [isFetched, setStreamedMessages]);

  // useEffect(() => {
  //   console.log("Stream changed:", stream);
  //   if (stream?.messages) {
  //     console.log("Setting streamed messages, current:", streamedMessages);
  //     setStreamedMessages(prevMessages => {
  //       const newMessages = stream.status === "inflight" ? 
  //         mergeMessagesById(prevMessages, stream.messages as TMessage[]) :
  //         stream.messages as TMessage[];
  //       console.log("New streamed messages:", newMessages);
  //       return newMessages;
  //     });
  //   }
  // }, [stream?.messages, stream?.status, setStreamedMessages]);
  // useEffect(() => {
  //   if (stream?.messages) {
  //     setStreamedMessages(stream.messages as TMessage[])
  //   }
  // }, [setStreamedMessages, stream?.messages])

  const messages = threadData?.values ? threadData.values : null;
  const streamMessages = stream?.messages as TMessage[] | undefined;

  return {
    messages: mergeMessagesById(messages, streamMessages),
    next: threadData?.next || [],
    refreshMessages: refetch
  };
}
