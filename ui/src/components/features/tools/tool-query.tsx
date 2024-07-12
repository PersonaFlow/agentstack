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
    <div className="flex px-2 b-2">
      <h2>
        <List /> Query: {query}
      </h2>
      <h2>
        <Search /> Using: {tool}
      </h2>
    </div>
  );
}
