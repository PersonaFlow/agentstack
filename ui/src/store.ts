import { PrimitiveAtom, atom } from "jotai";
import {
  TAssistant,
  TConversation,
  TMessage,
  TThread,
} from "./data-provider/types";

export const assistantAtom = atom<TAssistant | null>(null);
export const conversationAtom: PrimitiveAtom<TMessage[]> = atom([]);
