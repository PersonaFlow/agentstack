"use client";
import Spinner from "@/components/ui/spinner";
import {
  useCreateThread,
  useGetMyThreads,
} from "@/data-provider/query-service";
import { cn } from "@/utils/utils";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { useEffect, useState } from "react";
import NewThreadBtn from "./new-thread-btn";
import { useRouter } from "next/navigation";
import ThreadItem from "./thread-item";
import { TGroupedThreads, TThread } from "@/data-provider/types";
import { useToast } from "@/components/ui/use-toast";
import { useAtom } from "jotai";
import { assistantAtom } from "@/store";

export default function Navbar() {
  const { data: threadsData, isLoading: threadsLoading } =
    useGetMyThreads(true);

  const [filteredThreads, setFilteredThreads] = useState(threadsData || {});
  const [open, setOpen] = useState(false);
  const [selectedAssistant, setSelectedAssistant] = useAtom(assistantAtom);

  const router = useRouter();
  const createNewThread = useCreateThread();

  const { toast } = useToast();

  useEffect(() => {
    if (!selectedAssistant && threadsData) {
      setFilteredThreads(threadsData);
    }
  }, [threadsData]);

  useEffect(() => {
    if (selectedAssistant && threadsData) {
      // @ts-ignore
      const _filteredThreads = filterThreads(threadsData);
      setFilteredThreads(_filteredThreads);
    }
  }, [selectedAssistant, threadsData]);

  const filterThreads = (groupedThreads: TGroupedThreads) =>
    Object.entries(groupedThreads).reduce(
      (newGroupedThreads, [grouping, threads]) => {
        const filtered = threads.filter(
          (thread) => thread.assistant_id === selectedAssistant?.id,
        );
        // @ts-ignore
        newGroupedThreads[grouping] = filtered;
        return newGroupedThreads;
      },
      {},
    );

  const onNewThreadClick = () => {
    if (!selectedAssistant)
      return toast({
        variant: "destructive",
        title: "Please select an assistant before creating a new thread.",
      });

    createNewThread.mutate(
      {
        assistant_id: selectedAssistant?.id as string,
        name: "New thread",
        // @ts-ignore
        user_id: "1234",
      },
      {
        onSuccess: (thread: TThread) => {
          router.push(`/c/${thread.id}`);
        },
      },
    );
  };

  return (
    <div className="flex h-full border-2">
      {/* Container */}
      <div
        className={cn("flex flex-col m-3", open ? "w-72" : "w-0 collapse m-0")}
      >
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
            Object.entries(filteredThreads).map(([groupName, threads]) => {
              // @ts-ignore
              if (threads && threads.length > 0) {
                return (
                  <div key={groupName}>
                    <h2 className="m-3 text-gray-400">{groupName}</h2>
                    {/* @ts-ignore */}
                    {threads?.map((thread) => (
                      <ThreadItem key={thread.id} thread={thread} />
                    ))}
                  </div>
                );
              }
              return false;
            })
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
