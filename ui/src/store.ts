import { atom } from 'jotai'
import { TMessage } from './data-provider/types'

export const messagesAtom = atom<TMessage[]>([]);