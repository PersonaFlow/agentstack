'use client';

import { QueryKeys } from "@/data-provider/query-service";
import { TFileIngest, TFileStreamStatus, TStreamProgressState } from "@/data-provider/types";
import { fetchEventSource } from "@microsoft/fetch-event-source";
import { useQueryClient } from "@tanstack/react-query";
import { useCallback, useState } from "react";

export const useFileStream = () => {
  const [currentState, setCurrentState] = useState<TStreamProgressState | null>(
    null,
  );

  const queryClient = useQueryClient();

  const isStreaming = currentState?.status === TFileStreamStatus.inflight;

  const startProgressStream = useCallback(async ({ task_id }: TFileIngest) => {
    const controller = new AbortController();
    setCurrentState({ status: TFileStreamStatus.inflight });

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
            setCurrentState(() => ({
              status: TFileStreamStatus.inflight,
              progress,
            }));
          } else if (msg.event === TFileStreamStatus.error) {
            setCurrentState({
              status: TFileStreamStatus.error,
              progress: "Something went wrong."
            });
          }
        },
        onclose() {
          setCurrentState((currentState) => ({
            status:
              currentState?.status === TFileStreamStatus.error ? currentState.status : TFileStreamStatus.done,
            progress: currentState?.status === TFileStreamStatus.error ? "Something went wrong." : currentState?.progress
          }));
          queryClient.invalidateQueries({
            queryKey: [QueryKeys.assistantFiles],
          });
        },
        onerror(error) {
          setCurrentState({status: TFileStreamStatus.error});
        },
      },
    );
  }, []);

  return {
    startProgressStream,
    progressStream: currentState,
    isStreaming,
  };
};