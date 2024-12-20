'use client'
import { useState } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { AssistantBuilder } from './assistant-builder'

export default function BuildPanel() {
  const [isOpen, setIsOpen] = useState(true)

  const drawerStyles = {
    open: 'p-4 h-full flex flex-col gap-4 overflow-x-hidden sm:min-w-[520px]',
    closed: 'hidden',
  }

  return (
    <div className="flex items-center bg-slate-100 text-black rounded" data-testid="build-panel">
      <div className=" p-1">
        {isOpen ? (
          <ChevronRight className="cursor-pointer" onClick={() => setIsOpen((prev) => !prev)} />
        ) : (
          <ChevronLeft className="cursor-pointer" onClick={() => setIsOpen((prev) => !prev)} />
        )}
      </div>
      <div className={isOpen ? drawerStyles['open'] : drawerStyles['closed']}>
        <AssistantBuilder />
      </div>
    </div>
  )
}
