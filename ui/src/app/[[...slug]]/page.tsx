// 'use client'

import ChatPanel from "@/components/features/chat-panel";
import { isValidParam } from "@/lib/utils";
import { notFound } from "next/navigation";

export default function ConversationPage({params}: {params: {slug?: string[]}}) {

  console.log(params);

  if (!isValidParam(params.slug)) return notFound();

  return (
    <div className="border-solid border-2 w-full gap-4 flex flex-col">
      {/* <ChatPanel /> */}
    </div>
  );
}
