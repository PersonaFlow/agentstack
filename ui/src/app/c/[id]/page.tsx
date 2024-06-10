import { useUserThreads } from "@/data-provider/query-service";

export default function Page({ params }: { params: { id: string } }) {
  const { id: threadId } = params;
  const { data: threads } = useUserThreads("1234");

  return <div>{threads?.map((thread) => thread.name)}</div>;
}
