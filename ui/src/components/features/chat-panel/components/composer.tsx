'use client'
import { Input } from '@/components/ui/input'
import { Send, StopCircle } from 'lucide-react'
import { ChangeEvent } from 'react'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { Button } from '@/components/ui/button'

type Props = {
  onChange: (e: ChangeEvent<HTMLInputElement>) => void
  onSend: () => void
  value: string
  disabled?: boolean
  onStop: () => void
  isStreaming: boolean
}

export function Composer({ onChange, onSend, value, disabled, isStreaming, onStop }: Props) {
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (isStreaming) return

    if (e.key === 'Enter') {
      if (e.shiftKey) return

      e.preventDefault()
      onSend()
    }
  }

  return (
    <div className="mt-auto flex items-center m-3">
      <TooltipProvider>
        <Tooltip delayDuration={0}>
          <TooltipTrigger asChild>
            <Input
              endIcon={
                <Button onClick={isStreaming ? onStop : onSend} variant="ghost">
                  {isStreaming ? <StopCircle size={18} /> : <Send size={18} />}
                </Button>
              }
              onChange={onChange}
              value={value}
              onKeyDown={handleKeyDown}
              disabled={disabled}
            />
          </TooltipTrigger>
          {disabled && (
            <TooltipContent>
              <p>Select an assistant to start a new thread.</p>
            </TooltipContent>
          )}
        </Tooltip>
      </TooltipProvider>
    </div>
  )
}
