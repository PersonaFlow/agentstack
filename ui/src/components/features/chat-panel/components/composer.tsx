"use client";
import { Input } from "@/components/ui/input";
import { Send } from "lucide-react";
import { ChangeEvent } from "react";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

type Props = {
  onChange: (e: ChangeEvent<HTMLInputElement>) => void;
  sendMessage: () => void;
  value: string;
  disabled?: boolean;
};

export function Composer({ onChange, sendMessage, value, disabled }: Props) {
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      if (e.shiftKey) return;

      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="mt-auto flex items-center m-3">
      <TooltipProvider>
        <Tooltip delayDuration={0}>
          <TooltipTrigger asChild>
            <Input
              endIcon={Send}
              onChange={onChange}
              value={value}
              onKeyDown={handleKeyDown}
              disabled={disabled}
            />
          </TooltipTrigger>
          <TooltipContent>
            <p>Select an assistant to start a new thread.</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    </div>
  );
}
