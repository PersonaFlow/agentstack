"use client";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Checkbox } from "@/components/ui/checkbox";
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
} from "@/components/ui/form";
import { useRunnableConfigSchema } from "@/data-provider/query-service";
import { TTool } from "@/data-provider/types";
import { useConfigSchema } from "@/hooks/useConfig";
import { UseFormReturn } from "react-hook-form";

type TSelectCapabilitiesProps = {
  form: UseFormReturn<any>;
};

const options = [
  "retrieval",
  // { display: "Code interpretor", value: "Code interpretor" },
];

export default function SelectCapabilities({ form }: TSelectCapabilitiesProps) {
  const { availableTools } = useConfigSchema();
  const { type: architectureType } = form.getValues().config.configurable;

  console.log(availableTools);

  const capabilities = availableTools?.filter((tool) =>
    options.includes(tool.id),
  );

  const isChatRetrieval = (checkboxValue: string) =>
    architectureType === "chat_retrieval" && checkboxValue === "retrieval";

  return (
    <Accordion type="multiple">
      <AccordionItem value="Assistant Builder">
        <AccordionTrigger className="p-2">Capabilities</AccordionTrigger>
        <AccordionContent className="overflow-y-scroll p-2 flex flex-col gap-3">
          {capabilities?.map((capability) => (
            <FormField
              key={capability.id}
              control={form.control}
              name="config.configurable.tools"
              render={({ field }) => {
                return (
                  <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                    <FormControl>
                      <Checkbox
                        disabled={isChatRetrieval(capability.id)}
                        checked={
                          field.value?.some(
                            (selection: TTool) =>
                              selection.id === capability.id,
                          ) || isChatRetrieval(capability.id)
                        }
                        onCheckedChange={(checked) => {
                          return checked
                            ? field.onChange([...field.value, capability])
                            : field.onChange(
                                field.value?.filter(
                                  (selection: TTool) =>
                                    selection.id !== capability.id,
                                ),
                              );
                        }}
                      />
                    </FormControl>
                    <FormLabel className="text-sm font-normal">
                      {capability.name}
                    </FormLabel>
                  </FormItem>
                );
              }}
            />
          ))}
        </AccordionContent>
      </AccordionItem>
    </Accordion>
  );
}
