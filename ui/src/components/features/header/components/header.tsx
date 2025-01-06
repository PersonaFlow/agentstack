'use client'
import { Button } from '@/components/ui/button'
import { AssistantSelector } from '../../build-panel/components/assistant-selector'
import { useRouter } from 'next/navigation'
import { Plus } from 'lucide-react'
import PersonaFlowIcon from '../../../../../assets/PersonaFlowIcon-512.png'
import Image from 'next/image'

export default function Header() {
  const router = useRouter()
  const createAssistantStyle =
    'm-auto flex h-9 text-sm cursor-pointer items-center gap-2 rounded-md border border-white/50 px-3 py-4 text-md text-white transition-colors duration-200 hover:bg-gray-500/40'

  return (
    <div className="flex gap-2 m-2 justify-between">
      <div className="flex gap-4 items-center">
        {/* <Image className="rounded" src={PersonaFlowIcon} alt="PersonaFlow logo" width={40} height={40}/> */}
        <h1 className="text-slate-300 ml-6 text-xl">AgentStack</h1>
      </div>
      <div className="flex gap-2">
        <AssistantSelector />
        <a className={createAssistantStyle} onClick={() => router.push('/')}>
          <Plus className="ml-0" />
          <span className="ml-0">Create Assistant</span>
        </a>
        {/* <Button className="bg-slate-600 outline text-white flex gap-2" onClick={() => router.push("/")}>
          <Plus />
          Create Assistant
        </Button> */}
      </div>
    </div>
  )
}
