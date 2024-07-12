import { Button } from "@/components/ui/button";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { TMessage, TToolResult } from "@/data-provider/types";
import { CaretSortIcon } from "@radix-ui/react-icons";
import { useState } from "react";

export function ToolResult({ toolResult }: { toolResult: TMessage }) {
  const [isOpen, setIsOpen] = useState(false);

  console.log(toolResult);

  return (
    <div className="flex flex-col py-2 px-3 text-base md:px-4 mr-auto w-3/4 md:px-5 lg:px-1 xl:px-5 flex-col gap-4">
      <Collapsible open={isOpen} onOpenChange={setIsOpen}>
        <div className="flex items-center justify-between">
          <CollapsibleTrigger asChild>
            <Button variant="ghost" type="button" className="gap-2 mb-2">
              <span>Tool results: {toolResult.name}</span>
              <CaretSortIcon className="h-5 w-5" />
            </Button>
          </CollapsibleTrigger>
        </div>
        <CollapsibleContent className="space-y-2">
          {Array.isArray(toolResult.content)
            ? toolResult.content.map((item) => (
                <div className="rounded-md border px-4 py-2 font-mono text-sm shadow-sm">
                  {item.url}
                </div>
              ))
            : toolResult.content}
        </CollapsibleContent>
      </Collapsible>
    </div>
  );
}
