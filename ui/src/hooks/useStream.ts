import { TMessage, TStreamState } from "@/data-provider/types";
import { fetchEventSource } from "@microsoft/fetch-event-source";
import { useCallback, useState } from "react";

export const useStream = () => {
  const [current, setCurrent] = useState<TStreamState | null>(null);
  const [controller, setController] = useState<AbortController | null>(null);

  const startStream = useCallback(
    async (
      input: TMessage[] | Record<string, any> | null,
      thread_id: string,
      config?: Record<string, unknown>,
    ) => {
      const controller = new AbortController();
      setController(controller);
      setCurrent({ status: "inflight", messages: input || [] });

      console.log(input);

      await fetchEventSource("/runs/stream", {
        signal: controller.signal,
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input, thread_id, config }),
        openWhenHidden: true,
        onmessage(msg) {
          if (msg.event === "data") {
            const messages = JSON.parse(msg.data);
            setCurrent((current) => ({
              status: "inflight" as TStreamState["status"],
              messages: mergeMessagesById(current?.messages, messages),
              run_id: current?.run_id,
            }));
          } else if (msg.event === "metadata") {
            const { run_id } = JSON.parse(msg.data);
            setCurrent((current) => ({
              status: "inflight",
              messages: current?.messages,
              run_id: run_id,
            }));
          } else if (msg.event === "error") {
            setCurrent((current) => ({
              status: "error",
              messages: current?.messages,
              run_id: current?.run_id,
            }));
          }
        },
        onclose() {
          setCurrent((current) => ({
            status: current?.status === "error" ? current.status : "done",
            messages: current?.messages,
            run_id: current?.run_id,
          }));
          setController(null);
        },
        onerror(error) {
          setCurrent((current) => ({
            status: "error",
            messages: current?.messages,
            run_id: current?.run_id,
          }));
          setController(null);
          throw error;
        },
      });
    },
    [],
  );

  const stopStream = useCallback(
    (clear: boolean = false) => {
      controller?.abort();
      setController(null);
      if (clear) {
        setCurrent((current) => ({
          status: "done",
          run_id: current?.run_id,
        }));
      } else {
        setCurrent((current) => ({
          status: "done",
          messages: current?.messages,
          run_id: current?.run_id,
        }));
      }
    },
    [controller],
  );

  return {
    startStream,
    stopStream,
    stream: current,
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
