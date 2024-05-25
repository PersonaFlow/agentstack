'use client'
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useAssistants } from "@/data-provider/query-service"
import { QueryClient } from "@tanstack/react-query"
import * as dataService from "../data-provider/data-service";


// export async function getStaticProps() {
//     const queryClient = new QueryClient()
  
//     // await queryClient.prefetchQuery({ queryKey: ['posts'], queryFn: getPosts })
//     await queryClient.prefetchQuery({ queryKey: ['assistants'], queryFn: dataService.getAssistants()})
  
//     return {
//       props: {
//         dehydratedState: dehydrate(queryClient),
//       },
//     }
//   }

export default function Sidebar() {
    const { data } = useAssistants()

    return <div>
        <Tabs defaultValue="assistants" className="w-[400px] border-solid border-2 h-full flex justify-center">
            <TabsList>
                <TabsTrigger value="assistants">Assistants</TabsTrigger>
                <TabsTrigger value="chats">Chat</TabsTrigger>
            </TabsList>
            <TabsContent value="account">Make changes to your account here.</TabsContent>
            <TabsContent value="password">Change your password here.</TabsContent>
        </Tabs>

        <div>
            {
                // data?.map(item => <h1>{item.name}</h1>)
            }
        </div>
        </div>
}