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

const actions = [{}];

type TSelectActionsProps = {
  form: UseFormReturn<any>;
};

export default function SelectActions({ form }: TSelectActionsProps) {
  return (
    <Accordion type="multiple">
      <AccordionItem value="Options">
        <AccordionTrigger className="p-2">Actions</AccordionTrigger>
        <AccordionContent className="overflow-y-scroll p-2 flex flex-col gap-3">
          {/* {actions.map((action) => (
            <FormField
              key={action.value}
              control={form.control}
              name={action.name}
              render={({ field }) => {
                return (
                  <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                    <FormControl>
                      <Checkbox
                        checked={field.value?.includes(action.value)}
                        onCheckedChange={(checked) => {
                          return checked
                            ? field.onChange([...field.value, action.value])
                            : field.onChange(
                                field.value?.filter(
                                  (value: string) => value !== action.value,
                                ),
                              );
                        }}
                      />
                    </FormControl>
                    <FormLabel className="text-sm font-normal">
                      {action.display}
                    </FormLabel>
                  </FormItem>
                );
              }}
            />
          ))} */}
        </AccordionContent>
      </AccordionItem>
    </Accordion>
  );
}
