"use client";
import Spinner from "@/components/ui/spinner";
import {
  useGetMyThreads,
} from "@/data-provider/query-service";
import { cn } from "@/utils/utils";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { useEffect, useState } from "react";
import ThreadItem from "./thread-item";
import { TGroupedThreads } from "@/data-provider/types";
import { useSlugRoutes } from "@/hooks/useSlugParams";

export default function Navbar() {
  const { data: threadsData, isLoading: threadsLoading } =
    useGetMyThreads(true);

  const [filteredThreads, setFilteredThreads] = useState(threadsData || {});
  const [open, setOpen] = useState(false);

  const {assistantId} = useSlugRoutes()

  useEffect(() => {
    if (assistantId && threadsData) {
      let _filteredThreads = assistantId ? filterThreads(threadsData as TGroupedThreads) : threadsData;
      setFilteredThreads(_filteredThreads);
    }
  }, [assistantId, threadsData]);

  const filterThreads = (groupedThreads: TGroupedThreads) =>
    Object.entries(groupedThreads).reduce(
      (newGroupedThreads, [grouping, threads]) => {
        const filtered = threads.filter(
          (thread) => thread.assistant_id === assistantId,
        );
        // @ts-ignore
        newGroupedThreads[grouping] = filtered;
        return newGroupedThreads;
      },
      {},
    );

  return (
    <div className="flex h-full border-2">
      {/* Container */}
      <div
        className={cn("flex flex-col m-3", open ? "w-72" : "w-0 collapse m-0")}
      >
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
