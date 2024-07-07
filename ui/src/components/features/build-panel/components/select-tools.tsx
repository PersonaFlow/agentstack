"use client";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { FormControl, FormField, FormItem } from "@/components/ui/form";
import { UseFormReturn, useFieldArray } from "react-hook-form";
import { ToolDialog } from "./tool-dialog";
import { CircleX } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { TTool } from "@/data-provider/types";

type TSelectToolsProps = {
  form: UseFormReturn<any>;
};

export default function SelectTools({ form }: TSelectToolsProps) {
  const { remove } = useFieldArray({
    name: "config.configurable.tools",
    control: form.control,
  });

  const { tools } = form.getValues().config.configurable;

  return (
    <Accordion type="multiple">
      <AccordionItem value="Assistant Builder">
        <AccordionTrigger className="p-2">Tools</AccordionTrigger>
        <AccordionContent className="overflow-y-scroll p-2 flex flex-col gap-3">
          <div className="flex gap-2 flex-wrap">
            {tools.map((tool: TTool, index: number) => {
              return (
                <FormField
                  key={tool.id}
                  control={form.control}
                  name="config.configurable.tools"
                  render={({ field }) => {
                    return (
                      <FormItem>
                        <FormControl>
                          <Badge
                            className="rounded-full flex cursor-pointer text-xs gap-2"
                            onClick={() => remove(index)}
                          >
                            <p>{tool.name}</p>
                            <CircleX className="w-4" />
                          </Badge>
                        </FormControl>
                      </FormItem>
                    );
                  }}
                />
              );
            })}
          </div>
          <div className="mr-auto mt-6">
            <ToolDialog form={form} />
          </div>
        </AccordionContent>
      </AccordionItem>
    </Accordion>
  );
}
