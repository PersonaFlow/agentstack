import {
  QueryKeys,
  useUser,
  useUserThreads,
} from "@/data-provider/query-service";
import {
  DehydratedState,
  HydrationBoundary,
  QueryClient,
  dehydrate,
} from "@tanstack/react-query";
import * as dataService from "../../../data-provider/data-service";
import Conversation from "@/app/features/conversation/components/conversation";

export default async function ConversationPage({
  params,
  dehydratedState,
}: {
  params: { id: string };
  dehydratedState: DehydratedState;
}) {
  const queryClient = new QueryClient();

  await queryClient.prefetchQuery({
    queryKey: [QueryKeys.userThreads, "1234"],
    queryFn: await dataService.getUserThreads({
      userId: "1234",
    }),
  });

  const { id: threadId } = params;

  return (
    <main>
      <HydrationBoundary state={dehydratedState}>
        <Conversation />
      </HydrationBoundary>
    </main>
  );
}
