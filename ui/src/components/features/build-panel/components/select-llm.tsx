"use client";

import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
} from "@/components/ui/form";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { UseFormReturn } from "react-hook-form";

type TSelectLLMProps = {
  form: UseFormReturn<any>;
  llms: string[]
};

export function SelectLLM({ form, llms }: TSelectLLMProps) {
  return (
    <FormField
      control={form.control}
      name="config.configurable.llm_type"
      render={({ field }) => (
        <FormItem className="flex flex-col">
          <FormLabel>LLM Type</FormLabel>
          <FormControl>
            <Select onValueChange={field.onChange} defaultValue={field.value}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="LLM Type" />
              </SelectTrigger>
              <SelectContent>
                {llms.map((item) => (
                  <SelectItem key={item} value={item}>
                    {item}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </FormControl>
        </FormItem>
      )}
    />
  );
}
