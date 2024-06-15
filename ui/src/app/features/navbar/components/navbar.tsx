"use client";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useAssistants } from "@/data-provider/query-service";

export default function Navbar() {
  const { data } = useAssistants();

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
