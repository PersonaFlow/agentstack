import { atom } from "jotai";
import { TAssistant } from "./data-provider/types";

export const assistantAtom = atom<TAssistant | null>(null);
