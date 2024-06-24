import { PrimitiveAtom, atom } from "jotai";
import { TAssistant, TMessage } from "./data-provider/types";

export const assistantAtom = atom<TAssistant | null>(null);
export const conversationAtom: PrimitiveAtom<TMessage[]> = atom([]);
