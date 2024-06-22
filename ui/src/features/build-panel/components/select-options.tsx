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

type TSelectOptionsProps = {
  form: UseFormReturn<any>;
};

const options = [
  {
    display: "Interrupt before action",
    value: "interrupt_before_action",
    name: "config.configurable.interrupt_before_action",
  },
];

export default function SelectOptions({ form }: TSelectOptionsProps) {
  return (
    <Accordion type="multiple">
      <AccordionItem value="Options">
        <AccordionTrigger className="p-2">Options</AccordionTrigger>
        <AccordionContent className="overflow-y-scroll p-2 flex flex-col gap-3">
          {options.map((option) => (
            <FormField
              key={option.value}
              control={form.control}
              name={option.name}
              render={({ field }) => {
                return (
                  <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                    <FormControl>
                      <Checkbox
                        checked={field.value}
                        onCheckedChange={() => field.onChange(!field.value)}
                      />
                    </FormControl>
                    <FormLabel className="text-sm font-normal">
                      {option.display}
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
