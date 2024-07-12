import { TToolCall } from "@/data-provider/types";
import ToolQuery from "./tool-query";

type TToolContainer = {
  toolCalls: TToolCall[];
};

export default function ToolContainer({ toolCalls }: TToolContainer) {
  return (
    <div className="flex flex-col py-2 px-3 text-base md:px-4 my-4 mr-auto w-3/4 md:px-5 lg:px-1 xl:px-5 flex-col gap-4">
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
