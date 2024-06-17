"use client";
import { Button } from "@/components/ui/button";
import Spinner from "@/components/ui/spinner";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useAssistants, useUserThreads } from "@/data-provider/query-service";
import { cn } from "@/lib/utils";
import { Brain, ChevronLeft, ChevronRight } from "lucide-react";
import { useState } from "react";
import NewThreadBtn from "./new-thread-btn";
import { useRouter } from "next/navigation";
import ThreadItem from "./thread-item";
import { AssistantSelector } from "../../build-panel/components/assistant-selector";
import { TAssistant } from "@/data-provider/types";

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const [selectedAssistant, setSelectedAssistant] = useState<TAssistant>();
  const { data: threads, isLoading: threadsLoading } = useUserThreads("1234");
  const { data } = useAssistants();

  const router = useRouter();

  const onNewThreadClick = () => {
    const threadId = "1234";

    router.push(`/c/${threadId}`);
  };

  return (
    <div className="flex h-full border-2">
      {/* Container */}
      <div
        className={cn("flex flex-col m-3", open ? "w-72" : "w-0 collapse m-0")}
      >
        <div className="py-3">
          <AssistantSelector setSelectedAssistant={setSelectedAssistant} />
        </div>
        {/* New Thread Link */}
        {!threadsLoading && <NewThreadBtn handleClick={onNewThreadClick} />}
        <nav className="overflow-y-auto">
          {/* Threads loading */}
          {threadsLoading ? (
            <div className="flex flex-col items-center justify-center h-full">
              <Spinner />
              <p className="mt-3">Loading threads... </p>
            </div>
          ) : (
            // Object.entries(groupedThreadsState).map(([groupName, threads]) => {
            // if (threads && threads.length > 0) {
            // return (
            <div>
              <h2 className="m-3 text-gray-400">Group</h2>
              {threads?.map((thread) => (
                <ThreadItem key={thread.id} thread={thread} />
              ))}
            </div>
            // );
            // }
            // return false;
            // })
          )}
        </nav>
      </div>
      {/* Toggle Sidebar */}
      <div className="self-center hover:cursor-pointer p-1">
        {open ? (
          <ChevronLeft onClick={() => setOpen(false)} color="#000" />
        ) : (
          <ChevronRight onClick={() => setOpen(true)} color="#000" />
        )}
      </div>
    </div>
  );
}
