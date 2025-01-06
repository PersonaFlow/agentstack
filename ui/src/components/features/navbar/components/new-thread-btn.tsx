import { Button } from '@/components/ui/button'
import { Plus, PlusSquareIcon } from 'lucide-react'

type TNewThreadBtnProps = {
  handleClick: () => void
  disabled?: boolean
}

export default function NewThreadBtn({ handleClick, disabled }: TNewThreadBtnProps) {
  const newChatStyle =
    'm-auto flex h-12 cursor-pointer items-center gap-2 rounded-md border border-white/50 px-3 py-3 text-md text-white transition-colors duration-200 hover:bg-gray-500/40'

  return (
    <div className="mb-2 mx-2" style={{ width: 'calc(100% - 20px)' }}>
      <a className={newChatStyle} onClick={handleClick}>
        <Plus className="ml-2" />
        <span className="ml-1">New Chat</span>
      </a>
    </div>
  )
}
