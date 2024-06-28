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

const llmTypes = [
  { display: "GPT 3.5 Turbo", value: "GPT 3.5 Turbo" },
  { display: "GPT 4", value: "GPT 4" },
  { display: "GPT 4 (Azure OpenAI)", value: "GPT 4 (Azure OpenAI)" },
  { display: "Claude 2", value: "Claude 2" },
  { display: "Claude 2 (Amazon Bedrock)", value: "Claude 2 (Amazon Bedrock)" },
  { display: "GEMINI", value: "GEMINI" },
  { display: "Ollama", value: "Ollama" },
  { display: "Mixtral", value: "Mixtral" },
];

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
                {llmTypes.map((item) => (
                  <SelectItem key={item.value} value={item.display}>
                    {item.value}
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
