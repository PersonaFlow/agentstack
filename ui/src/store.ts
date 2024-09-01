import { atom } from 'jotai'
import { TMessage } from './data-provider/types'

export const messagesAtom = atom<TMessage[]>([]);
export const threadAtom = atom<boolean>(false);