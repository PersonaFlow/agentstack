'use client';

import { QueryKeys } from "@/data-provider/query-service";
import { TFileIngest, TStreamProgressState } from "@/data-provider/types";
import { fetchEventSource } from "@microsoft/fetch-event-source";
import { useQueryClient } from "@tanstack/react-query";
import { useCallback, useEffect, useState } from "react";

// TODO - figure out how to create one instance of the hook
// -> then you can display response in file tab

// Todo - figure out what the stream response looks like
// export type TStreamState = {
//   status: "inflight" | "error" | "done";
//   messages?: TMessage[] | Record<string, any>;
//   run_id?: string;
//   thread_id?: string;
// };

// curl http://127.0.0.1:9000/api/v1/rag/ingest/{taskId}/progress

export const useFileStream = () => {
  const [currentState, setCurrentState] = useState<TStreamProgressState | null>(
    null,
  );
  const [controller, setController] = useState<AbortController | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);

  const queryClient = useQueryClient();

  useEffect(() => {
    if (currentState?.status === "error" || currentState?.status === "done") {
      setIsStreaming(false);
    }
  }, [currentState]);

  const startProgressStream = useCallback(async ({ task_id }: TFileIngest) => {
    const controller = new AbortController();
    setController(controller);
    setCurrentState({ status: "inflight" });
    setIsStreaming(true);

    await fetchEventSource(
      `${process.env.NEXT_PUBLIC_BASE_API_URL}/api/v1/rag/ingest/${task_id}/progress`,
      {
        signal: controller.signal,
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          "X-API-KEY": "personaflow_api_key",
        },
        openWhenHidden: true,
        onmessage(msg) {
          if (msg.event === "data") {
            const progressData = JSON.parse(msg.data);
            const { progress } = progressData;
            console.log(progressData);
            setCurrentState((currentState) => ({
              status: "inflight" as TStreamProgressState["status"],
              progress,
            }));
          } else if (msg.event === "error") {
            setCurrentState((currentState) => ({
              status: "error",
            }));
          }
        },
        onclose() {
          setCurrentState((currentState) => ({
            status:
              currentState?.status === "error" ? currentState.status : "done",
          }));
          setController(null);
          queryClient.invalidateQueries({
            queryKey: [QueryKeys.assistantFiles],
          });
        },
        onerror(error) {
          setCurrentState((currentState) => ({
            status: "error",
          }));
          setController(null);
          throw error;
        },
      },
    );
  }, []);

  console.log(currentState)

  return {
    startProgressStream,
    progressStream: currentState,
    isStreaming,
  };
};