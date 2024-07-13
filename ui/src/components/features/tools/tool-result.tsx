import {
  Accordion,
  AccordionItem,
  AccordionTrigger,
  AccordionContent,
} from "@/components/ui/accordion";
import { Button } from "@/components/ui/button";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { TMessage } from "@/data-provider/types";
import { CaretSortIcon } from "@radix-ui/react-icons";
import { MoveUpRight } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

const AccordionToolContent = ({
  content,
  url,
}: {
  content: string;
  url: string;
}) => {
  return (
    <Accordion type="single" collapsible>
      <AccordionItem value={url}>
        <AccordionTrigger className="text-left">
          <div className="flex w-full">
            {url}
            <Button variant="outline" type="button" className="ml-auto mr-2">
              <Link
                href={url}
                target="_blank"
                className="flex gap-2 items-center"
              >
                Visit
                <MoveUpRight className="w-4 h-4" />
              </Link>
            </Button>
          </div>
        </AccordionTrigger>
        <AccordionContent>{content}</AccordionContent>
      </AccordionItem>
    </Accordion>
  );
};

export function ToolResult({ toolResult }: { toolResult: TMessage }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="flex flex-col py-2 px-3 text-base md:px-4 mr-auto w-3/4 md:px-5 lg:px-1 xl:px-5 flex-col gap-4">
      <Collapsible open={isOpen} onOpenChange={setIsOpen}>
        <div className="flex items-center justify-between">
          <CollapsibleTrigger asChild>
            <Button variant="outline" type="button" className="gap-2 mb-2">
              <span>Tool results: {toolResult.name}</span>
              <CaretSortIcon className="h-5 w-5" />
            </Button>
          </CollapsibleTrigger>
        </div>
        <CollapsibleContent className="space-y-2">
          {Array.isArray(toolResult.content)
            ? toolResult.content.map((item) => (
                <AccordionToolContent
                  url={item.url}
                  content={item.content}
                  key={item.url}
                />
              ))
            : toolResult.content}
        </CollapsibleContent>
      </Collapsible>
    </div>
  );
}
