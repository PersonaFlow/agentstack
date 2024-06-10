export default function Page({ params }: { params: { threadId: string } }) {
  console.log(params.threadId);
  return <h1>{params.threadId}</h1>;
}
