import { atom } from "jotai";

export const assistantAtom = atom(localStorage.getItem('personaflow_defaultAssistant') || null);
