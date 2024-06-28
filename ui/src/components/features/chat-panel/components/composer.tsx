"use client";
import { Input } from "@/components/ui/input";
import { Send } from "lucide-react";
import { ChangeEvent } from "react";

type Props = {
  onChange: (e: ChangeEvent<HTMLInputElement>) => void;
  sendMessage: () => void;
  value: string;
};

export function Composer({ onChange, sendMessage, value }: Props) {
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      // Do expected default behaviour (add a newline inside of the textarea)
      if (e.shiftKey) return;

      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="mt-auto flex items-center m-3">
      <Input
        endIcon={Send}
        onChange={onChange}
        value={value}
        onKeyDown={handleKeyDown}
      />
    </div>
  );
}
