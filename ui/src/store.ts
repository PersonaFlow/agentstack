import { atom } from "jotai";
import { TAssistant, TMessage, TThread } from "./data-provider/types";

export const assistantAtom = atom<TAssistant | null>(null);
export const conversationAtom = atom<TMessage[]>([]);
