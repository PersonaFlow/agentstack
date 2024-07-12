import { TToolCall } from "@/data-provider/types";
import ToolQuery from "./tool-query";

type TToolContainer = {
  toolCalls: TToolCall[];
};

export default function ToolContainer({ toolCalls }: TToolContainer) {
  return (
    <div className="flex flex-col">
      {toolCalls.map((toolCall) => (
        <ToolQuery
          query={toolCall.args.query}
          tool={toolCall.name}
          key={toolCall.id}
        />
      ))}
    </div>
  );
}
