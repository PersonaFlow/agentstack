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
import { UseFormReturn } from "react-hook-form";

type TSelectCapabilitiesProps = {
  form: UseFormReturn<any>;
};

const capabilities = [
  { display: "Retrieval", value: "Retrieval" },
  // { display: "Code interpretor", value: "Code interpretor" },
];

export default function SelectCapabilities({ form }: TSelectCapabilitiesProps) {
  const { type: architectureType } = form.getValues().config.configurable;

  const isChatRetrieval = (checkboxValue: string) =>
    architectureType === "chat_retrieval" && checkboxValue === "Retrieval";

  return (
    <Accordion type="multiple">
      <AccordionItem value="Assistant Builder">
        <AccordionTrigger className="p-2">Capabilities</AccordionTrigger>
        <AccordionContent className="overflow-y-scroll p-2 flex flex-col gap-3">
          {capabilities.map((capability) => (
            <FormField
              key={capability.value}
              control={form.control}
              name="config.configurable.tools"
              render={({ field }) => {
                return (
                  <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                    <FormControl>
                      <Checkbox
                        disabled={isChatRetrieval(capability.value)}
                        checked={
                          field.value?.includes(capability.value) ||
                          isChatRetrieval(capability.value)
                        }
                        onCheckedChange={(checked) => {
                          return checked
                            ? field.onChange([...field.value, capability.value])
                            : field.onChange(
                                field.value?.filter(
                                  (value: string) => value !== capability.value,
                                ),
                              );
                        }}
                      />
                    </FormControl>
                    <FormLabel className="text-sm font-normal">
                      {capability.display}
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
