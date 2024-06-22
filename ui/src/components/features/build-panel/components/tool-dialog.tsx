"use client";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
} from "@/components/ui/form";
import { UseFormReturn } from "react-hook-form";

// const tools = [
//   { display: "DDG Search", value: "DDG Search" },
//   { display: "Search (Tavily)", value: "Search (Tavily)" },
//   {
//     display: "Search (short answer, Tavily)",
//     value: "Search (short answer, Tavily)",
//   },
//   { display: "Retrieval", value: "Retrieval" },
//   { display: "Arxiv", value: "Arxiv" },
//   { display: "PubMed", value: "PubMed" },
//   { display: "Wikipedia", value: "Wikipedia" },
// ];

const tools = [
  "DDG Search",
  "Search (Tavily)",
  "Search (short answer, Tavily)",
  "Retrieval",
  "Arxiv",
  "PubMed",
  "Wikipedia",
];
type TToolDialog = {
  form: UseFormReturn<any>;
};

export function ToolDialog({ form }: TToolDialog) {
  return (
    <Dialog>
      <DialogTrigger>
        <Button className="rounded-xl">Add tool</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Tools</DialogTitle>
          <DialogDescription>
            {tools.map((tool) => (
              <FormField
                key={tool}
                control={form.control}
                name={`config.configurable.tools`}
                render={({ field }) => {
                  return (
                    <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                      <FormControl>
                        <Checkbox
                          checked={field.value?.includes(tool)}
                          onCheckedChange={(checked) => {
                            return checked
                              ? field.onChange([...field.value, tool])
                              : field.onChange(
                                  field.value?.filter(
                                    (value: string) => value !== tool,
                                  ),
                                );
                          }}
                        />
                      </FormControl>
                      <FormLabel className="text-sm font-normal">
                        {tool}
                      </FormLabel>
                    </FormItem>
                  );
                }}
              />
            ))}
          </DialogDescription>
        </DialogHeader>
      </DialogContent>
    </Dialog>
  );
}
