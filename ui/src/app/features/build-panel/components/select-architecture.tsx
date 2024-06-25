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

const architectureTypes = [
  { display: "Chat", value: "chatbot" },
  { display: "Chat with Retrieval", value: "chat_retrieval" },
  { display: "Agent", value: "agent" },
];

export default function SelectArchitecture({
  form,
  types,
}: {
  form: UseFormReturn<any>;
  types: string[];
}) {
  return (
    <FormField
      control={form.control}
      name="config.configurable.type"
      render={({ field }) => (
        <FormItem className="flex flex-col">
          <FormLabel>Architecture</FormLabel>
          <FormControl>
            <Select onValueChange={field.onChange} defaultValue={field.value}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Select architecture" />
              </SelectTrigger>
              <SelectContent>
                {types.map((item) => (
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
