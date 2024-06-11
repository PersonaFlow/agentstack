"use client";

import { useUserThreads } from "@/data-provider";
import { useEffect } from "react";

export default function Conversation() {
  const { data: threads } = useUserThreads({
    userId: "1234",
  });

  useEffect(() => {
    console.log(threads);
  }, [threads]);

  return (
    <div>
      {threads?.map((thread) => <h1 key={thread.id}>{thread.name}</h1>)}
    </div>
  );
}
