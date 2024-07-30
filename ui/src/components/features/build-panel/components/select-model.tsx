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

type TSelectModalProps = {
  form: UseFormReturn<any>;
  models: string[];
};

const modelTypes = [
  { display: "GPT 3.5 Turbo", value: "GPT 3.5 Turbo" },
  { display: "GPT 4 Turbo", value: "GPT 4 Turbo" },
  { display: "GPT 4 (Azure OpenAI)", value: "GPT 4 (Azure OpenAI)" },
  { display: "Claude 2", value: "Claude 2" },
  { display: "Claude 2 (Amazon Bedrock)", value: "Claude 2 (Amazon Bedrock)" },
  { display: "GEMINI", value: "GEMINI" },
  { display: "Ollama", value: "Ollama" },
];

export default function SelectModel({ form, models }: TSelectModalProps) {
  return (
    <FormField
      control={form.control}
      name="config.configurable.agent_type"
      render={({ field }) => (
        <FormItem className="flex flex-col">
          <FormLabel>Model</FormLabel>
          <FormControl>
            <Select onValueChange={field.onChange} defaultValue={field.value}>
              <SelectTrigger className="w-[180px]" aria-label="model">
                <SelectValue placeholder="Select Agent Type" />
              </SelectTrigger>
              <SelectContent>
                {modelTypes.map((item) => (
                  <SelectItem key={item.value} value={item.value}>
                    {item.display}
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
