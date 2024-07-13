import { List, Search } from "lucide-react";

const icons = [
  { title: "query", icon: <List /> },
  { title: "search", icon: <Search /> },
];

type TToolQueryProps = {
  query: string;
  tool: string;
};

export default function ToolQuery({ query, tool }: TToolQueryProps) {
  return (
    <>
      <h2 className="flex gap-2 rounded-sm border-2 p-2">
        <List /> Query: {query}
      </h2>
      <h2 className="flex gap-2 rounded-sm border-2 p-2">
        <Search /> Using: {tool}
      </h2>
    </>
  );
}
