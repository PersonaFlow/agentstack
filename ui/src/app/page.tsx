"use client";

import { ChatForm } from "@/components/features/chat-panel/components/chat-form";

export default function Page() {
  return (
    <div className="border-solid border-2 w-full gap-4 flex flex-col">
      <ChatForm />
    </div>
  );
}
