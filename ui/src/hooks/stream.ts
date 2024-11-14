import { TStreamStatus } from "@/data-provider/types";
import {
  resetStreamStateAtom,
  startStreamAtom,
  stopStreamAtom,
  streamStateAtom,
} from "@/store";
import { useAtomValue, useSetAtom } from "jotai/react";

export const useResetStreamState = () => {
  return useSetAtom(resetStreamStateAtom);
};

export const useStream = () => {
  return useAtomValue(streamStateAtom);
};

export const useIsStreaming = () => {
  const stream = useStream();

  return stream?.status === TStreamStatus.INFLIGHT;
};

export const useStreamThreadId = () => {
  const stream = useStream();

  return stream?.thread_id;
};

export const useIsStreamDone = () => {
  const stream = useStream();

  return stream?.status === TStreamStatus.DONE;
};

export const useIsStreamError = () => {
  const stream = useStream();
  return stream?.status === TStreamStatus.ERROR;
};

export const useStartStream = () => {
  return useSetAtom(startStreamAtom);
};

export const useStopStream = () => {
  return useSetAtom(stopStreamAtom);
};
