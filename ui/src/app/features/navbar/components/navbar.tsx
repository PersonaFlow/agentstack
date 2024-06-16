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

const threads = [
  { name: "thread one" },
  { name: "thread two" },
  { name: "thread three" },
  { name: "thread four" },
];

const ThreadSession = () => <div>New thread</div>;

export default function Navbar() {
  const [open, setOpen] = useState(false);
  // const { data: threads } = useUserThreads("1234");
  const { data } = useAssistants();

  const router = useRouter();

  const threadsLoading = false;

  const onNewThreadClick = () => {
    const threadId = "1234";

    router.push(`/c/${threadId}`);
  };
  // console.log(threads);

  return (
    <div className="flex h-full border-2">
      {/* Container */}
      <div
        className={cn("flex flex-col m-3", open ? "w-72" : "w-0 collapse m-0")}
      >
        {/* Header */}
        {/* <div className="flex items-center justify-start-w-full p-2 ml-2 mr-2">
          <Brain />
        </div> */}
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
              {threads.map((thread) => (
                <ThreadSession />
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

  return (
    <div className="p-4 border-solid border-2 h-full justify-center">
      <Tabs defaultValue="assistants">
        <TabsList>
          <TabsTrigger value="assistants">Assistants</TabsTrigger>
          <TabsTrigger value="chats">Chat</TabsTrigger>
        </TabsList>
        <TabsContent value="account">
          Make changes to your account here.
        </TabsContent>
        <TabsContent value="password">Change your password here.</TabsContent>
      </Tabs>

      <div>{data?.map((item) => <h1 key={item.name}>{item.name}</h1>)}</div>
    </div>
  );
}
