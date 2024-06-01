"use client";

import { ChatForm } from "./components/ChatForm";

export default function Page() {
  return (
    <div className="border-solid border-2 w-full gap-4 flex flex-col">
      <ChatForm />
    </div>
  );
}
