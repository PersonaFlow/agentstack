import { TMessage, TStreamState, TStreamStatus } from "@/data-provider/types";
import { streamAbortControllerAtom, streamStateAtom } from "@/store";
import {
  EventSourceMessage,
  fetchEventSource,
} from "@microsoft/fetch-event-source";
import { useAtom } from "jotai/react";
import { useCallback } from "react";

export type TStartStreamProps = {
  assistant_id: string;
  input: TMessage[] | Record<string, any> | null;
  thread_id?: string;
  user_id?: string;
};

export type TStartStreamFn = (
  props: TStartStreamProps & {
    options?: {
      onError: (e: unknown) => void;
    };
  },
) => Promise<void>;

export type TStopStreamFn = (props?: { clear?: boolean }) => void;

export const useStream = (): {
  startStream: TStartStreamFn;
  stopStream: TStopStreamFn;
  stream: TStreamState | null;
} => {
  const [streamState, setStreamState] = useAtom(streamStateAtom);
  const [controller, setController] = useAtom(streamAbortControllerAtom);

  /**
   * START STREAM
   */
  const startStream = useCallback(
    async ({
      input,
      thread_id,
      assistant_id,
      user_id,
      options,
    }: TStartStreamProps & { options?: { onError: (e: unknown) => void } }) => {
      const controller = new AbortController();
      setController(controller);
      setStreamState((prev) => ({
        status: TStreamStatus.INFLIGHT,
        messages: input === null ? prev?.messages || [] : [], // Keep messages for continuation
        thread_id: prev?.thread_id,
      }));

      return await runStream({
        abortController: controller,
        payload: { assistant_id, input, thread_id, user_id },
        eventHandlers: {
          onMessage(msg) {
            // console.log('Stream event received:', msg.event, msg.data);
            setStreamState((currentState) =>
              getNewStreamStateByEventMessage(msg, currentState),
            );
          },
          onClose() {
            setStreamState(getNewStreamStateOnClose);
            setController(null);
          },
          onError(error) {
            setStreamState(getNewStreamStateOnError);
            setController(null);
            options?.onError(error);
          },
        },
      });
    },
    [],
  );

  /**
   * STOP STREAM
   */
  const stopStream = useCallback(
    ({ clear }: { clear?: boolean } = { clear: false }) => {
      controller?.abort();
      setController(null);
      setStreamState((currentState) =>
        getNewStreamStateOnStop(currentState, clear),
      );
      // setIsStreaming(false);
    },
    [controller],
  );

  return {
    startStream,
    stopStream,
    stream: streamState,
    // isStreaming,
  };
};

export async function runStream({
  abortController,
  payload,
  eventHandlers,
}: {
  abortController: AbortController;
  payload: TStartStreamProps;
  eventHandlers: {
    onMessage: (msg: EventSourceMessage) => void;
    onClose: () => void;
    onError: (error: unknown) => void;
  };
}) {
  return await fetchEventSource(
    `${process.env.NEXT_PUBLIC_BASE_API_URL}/api/v1/runs/stream`,
    {
      signal: abortController.signal,
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-KEY": "personaflow_api_key",
      },
      body: JSON.stringify(payload),
      openWhenHidden: true,
      onmessage: eventHandlers.onMessage,
      onclose: eventHandlers.onClose,
      onerror: eventHandlers.onError,
    },
  );
}

export function getNewStreamStateOnError(
  currentStream: TStreamState | null,
): TStreamState | null {
  return {
    ...currentStream,
    status: TStreamStatus.ERROR,
  };
}

export function getNewStreamStateOnClose(
  currentStream: TStreamState | null,
): TStreamState | null {
  return {
    ...currentStream,
    status:
      currentStream?.status === TStreamStatus.ERROR
        ? currentStream.status
        : TStreamStatus.DONE,
  };
}

export function getNewStreamStateOnStop(
  currentStream: TStreamState | null,
  clear: boolean = false,
): TStreamState | null {
  return {
    ...currentStream,
    status: TStreamStatus.DONE,
    messages: clear ? [] : currentStream?.messages,
  };
}
export function getNewStreamStateByEventMessage(
  msg: EventSourceMessage,
  currentStream: TStreamState | null,
): TStreamState | null {
  if (msg.event === "error") {
    return {
      ...currentStream,
      status: TStreamStatus.ERROR,
    };
  }

  if (msg.event === "metadata") {
    const { run_id, thread_id } = JSON.parse(msg.data);
    return {
      ...currentStream,
      status: TStreamStatus.INFLIGHT,
      run_id: run_id,
      thread_id: thread_id,
    };
  }

  if (msg.event === "data") {
    const messages = JSON.parse(msg.data);
    return {
      ...currentStream,
      status: TStreamStatus.INFLIGHT,
      messages: mergeMessagesById(currentStream?.messages, messages),
    };
  }

  return currentStream;
}

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
