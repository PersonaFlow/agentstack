import { atom } from "jotai";
import { TMessage, TStreamState, TStreamStatus } from "./data-provider/types";
import {
  getNewStreamStateByEventMessage,
  mergeMessagesById,
  TStartStreamProps,
} from "./hooks/useStream";
import {
  EventSourceMessage,
  fetchEventSource,
} from "@microsoft/fetch-event-source";

export const messagesAtom = atom<TMessage[]>([]);
messagesAtom.debugLabel = "Stream Messages Atom";
export const mergedMessagesAtom = atom<TMessage[]>([]);

export const threadAtom = atom<boolean>(false);
export const streamAbortControllerAtom = atom<AbortController | null>(null);
export const streamStateAtom = atom<TStreamState | null>(null);
streamStateAtom.debugLabel = "Stream State Atom";

export const resetStreamStateAtom = atom(null, (get, set) => {
  set(streamStateAtom, null);
});
export const writeOnlyStreamAtom = atom(
  null,
  (get, set, update: TStreamState) => {
    set(streamStateAtom, update);
  },
);

/**
 * Stream Events related atoms
 */
export const onStreamMessageAtom = atom(
  null,
  (get, set, msg: EventSourceMessage) => {
    const currentStream = get(streamStateAtom);
    const updatedStream = getNewStreamStateByEventMessage(msg, currentStream);
    set(streamStateAtom, updatedStream);
  },
);

export const onStreamCloseAtom = atom(null, (_, set) => {
  set(streamAbortControllerAtom, null);
  set(streamStateAtom, (streamState) => ({
    ...streamState,
    status:
      streamState?.status === TStreamStatus.ERROR
        ? streamState.status
        : TStreamStatus.DONE,
  }));
});

export const onStreamErrorAtom = atom(null, (_, set) => {
  set(streamStateAtom, (streamState) => ({
    ...streamState,
    status: TStreamStatus.ERROR,
  }));
  set(streamAbortControllerAtom, null);
});

/**
 * Stream control atoms
 */
export const startStreamAtom = atom(
  null,
  async (
    get,
    set,
    {
      input,
      thread_id,
      assistant_id,
      user_id,
      options: { onError } = { onError: () => {} },
    }: TStartStreamProps & { options?: { onError: (e: unknown) => void } },
  ) => {
    const controller = new AbortController();
    set(streamAbortControllerAtom, controller);

    set(streamStateAtom, (currentState) => ({
      ...currentState,
      status: TStreamStatus.INFLIGHT,
      messages: input === null ? currentState?.messages || [] : [],
    }));

    await fetchEventSource(
      `${process.env.NEXT_PUBLIC_BASE_API_URL}/api/v1/runs/stream`,
      {
        signal: controller.signal,
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-KEY": "personaflow_api_key",
        },
        body: JSON.stringify({
          user_id,
          input,
          thread_id,
          assistant_id,
        }),
        openWhenHidden: true,
        onmessage(msg) {
          // console.log("Stream event received:", msg.event, msg.data);
          const currentStream = get(streamStateAtom);
          const updatedStream = getNewStreamStateByEventMessage(
            msg,
            currentStream,
          );
          set(streamStateAtom, updatedStream);
        },
        onclose() {
          set(streamAbortControllerAtom, null);
          set(streamStateAtom, (currentState) => ({
            ...currentState,
            status:
              currentState?.status === TStreamStatus.ERROR
                ? currentState.status
                : TStreamStatus.DONE,
          }));
        },
        onerror(error) {
          set(streamStateAtom, (currentState) => ({
            ...currentState,
            status: TStreamStatus.ERROR,
          }));
          set(streamAbortControllerAtom, null);
          onError?.(error);
        },
      },
    );
  },
);

export const stopStreamAtom = atom(
  null,
  (get, set, { clear }: { clear?: boolean } = { clear: false }) => {
    const controller = get(streamAbortControllerAtom);
    controller?.abort();
    set(streamAbortControllerAtom, null);
    set(streamStateAtom, (currentState) => ({
      ...currentState,
      status: TStreamStatus.DONE,
      messages: clear ? [] : currentState?.messages,
    }));
  },
);
