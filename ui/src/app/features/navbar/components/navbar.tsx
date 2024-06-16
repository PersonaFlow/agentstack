"use client";
import { Button } from "@/components/ui/button";
import Spinner from "@/components/ui/spinner";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useAssistants, useUserThreads } from "@/data-provider/query-service";
import { cn } from "@/lib/utils";
import { Brain, ChevronLeft, ChevronRight } from "lucide-react";
import { useState } from "react";

type TNewThreadBtn = {
  handleClick: () => void;
};

const threads = [
  { name: "thread one" },
  { name: "thread two" },
  { name: "thread three" },
  { name: "thread four" },
];

const NewThreadBtn = ({ handleClick }: TNewThreadBtn) => (
  <Button onClick={handleClick}>New thread</Button>
);

const ThreadSession = () => <div>New thread</div>;

export default function Navbar() {
  const [open, setOpen] = useState(false);
  // const { data: threads } = useUserThreads("1234");
  const { data } = useAssistants();

  const threadsLoading = false;

  const onNewThreadClick = () => {
    ("");
  };
  // console.log(threads);

  return (
    <div className="flex h-full top-0 content-center">
      {/* Container */}
      <div
        className={cn(
          "flex flex-col items-center",
          open ? "w-72" : "w-0 collapse",
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-start-w-full p-2 ml-2 mr-2">
          <Brain />
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
      <div>
        {open ? (
          <ChevronLeft onClick={() => setOpen(false)} color="#000" />
        ) : (
          <ChevronRight onClick={() => setOpen(false)} color="#000" />
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
