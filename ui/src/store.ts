import { PrimitiveAtom, atom } from "jotai";
import { TAssistant, TMessage, TThread } from "./data-provider/types";

export const assistantAtom = atom<TAssistant | null>(null);
export const conversationAtom: PrimitiveAtom<TMessage[]> = atom([]);
export const threadAtom = atom<TThread | null>(null);
