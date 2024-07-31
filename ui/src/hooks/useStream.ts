import { TMessage, TStreamState } from "@/data-provider/types";
import { fetchEventSource } from "@microsoft/fetch-event-source";
import { useCallback, useEffect, useState } from "react";
import { useSlugRoutes } from "./useSlugParams";
import { useAtom } from "jotai";
import { messagesAtom } from "@/store";

type TStartStreamProps = {
  input: TMessage[] | Record<string, any> | null;
  thread_id: string;
  assistant_id: string;
  user_id?: string;
  setIsNewThread: (arg: boolean) => void;
};

export const useStream = () => {
  const [currentState, setCurrentState] = useState<TStreamState | null>(null);
  const [controller, setController] = useState<AbortController | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const {threadId} = useSlugRoutes()

  useEffect(() => {
    if (currentState?.status === 'error' || currentState?.status === 'done') {
      setIsStreaming(false);
    }
  }, [currentState]);
  

  useEffect(() => {
    console.log(currentState?.messages);
    console.log(threadId)
  },[currentState])

  const startStream = useCallback(
    async ({ input, thread_id, assistant_id, user_id }: TStartStreamProps) => {
      const controller = new AbortController();
      setController(controller);
      setCurrentState({ status: "inflight", messages: [] });
      setIsStreaming(true);

      await fetchEventSource(
        `${process.env.NEXT_PUBLIC_BASE_API_URL}/api/v1/runs/stream`,
        {
          signal: controller.signal,
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-API-KEY": "personaflow_api_key",
          },
          body: JSON.stringify({ user_id, input, thread_id, assistant_id }),
          openWhenHidden: true,
          onmessage(msg) {
            if (msg.event === "data") {
              const messages = JSON.parse(msg.data);
              setCurrentState((currentState) => ({
                status: "inflight" as TStreamState["status"],
                messages: mergeMessagesById(currentState?.messages, messages),
                run_id: currentState?.run_id,
                thread_id: currentState?.thread_id
              }));
            } else if (msg.event === "metadata") {
              const { run_id, thread_id } = JSON.parse(msg.data);
              setCurrentState((currentState) => ({
                status: "inflight",
                messages: currentState?.messages,
                run_id: run_id,
                thread_id: thread_id
              }));
            } else if (msg.event === "error") {
              setCurrentState((currentState) => ({
                status: "error",
                messages: currentState?.messages,
                run_id: currentState?.run_id,
                thread_id: currentState?.thread_id
              }));
            }
          },
          onclose() {
            setCurrentState((currentState) => ({
              status: currentState?.status === "error" ? currentState.status : "done",
              messages: currentState?.messages,
              run_id: currentState?.run_id,
              thread_id: currentState?.thread_id
            }));
            setController(null);
          },
          onerror(error) {
            setCurrentState((currentState) => ({
              status: "error",
              messages: currentState?.messages,
              run_id: currentState?.run_id,
              thread_id: currentState?.thread_id
            }));
            setController(null);
            throw error;
          },
        },
      );
    },
    [],
  );

  const stopStream = useCallback(
    (clear: boolean = false) => {
      controller?.abort();
      setController(null);
      if (clear) {
        setCurrentState((currentState) => ({
          status: "done",
          run_id: currentState?.run_id,
          thread_id: currentState?.thread_id
        }));
      } else {
        setCurrentState((currentState) => ({
          status: "done",
          messages: currentState?.messages,
          run_id: currentState?.run_id,
          thread_id: currentState?.thread_id
        }));
      }
    },
    [controller],
  );

  return {
    startStream,
    stopStream,
    stream: currentState,
    isStreaming,
  };
};

export function mergeMessagesById(
  left: TMessage[] | Record<string, any> | null | undefined,
  right: TMessage[] | Record<string, any> | null | undefined,
): TMessage[] {
  const leftMsgs = Array.isArray(left) ? left : left?.messages;
  const rightMsgs = Array.isArray(right) ? right : right?.messages;

  const merged = (leftMsgs ?? [])?.slice();
  for (const msg of rightMsgs ?? []) {
    const foundIdx = merged.findIndex((m: any) => m.id === msg.id);
    if (foundIdx === -1) {
      merged.push(msg);
    } else {
      merged[foundIdx] = msg;
    }
  }
  return merged;
}
