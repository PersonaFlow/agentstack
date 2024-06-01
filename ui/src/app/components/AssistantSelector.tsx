"use client";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useAssistants } from "@/data-provider/query-service";
import { LoaderCircle } from "lucide-react";

type TAssistantProps = {
  selectedAssistant: string;
  setSelectedAssistant: (arg: string) => void;
};

export function AssistantSelector({
  selectedAssistant,
  setSelectedAssistant,
}: TAssistantProps) {
  const { data: assistantsData, isLoading } = useAssistants();

  if (!assistantsData || isLoading) return <LoaderCircle />;
  return (
    <div className="px-2">
      <Select
        onValueChange={(value) => setSelectedAssistant(value)}
        defaultValue={
          assistantsData.length > 0 ? assistantsData[0].name : selectedAssistant
        }
      >
        <SelectTrigger className="w-[180px]">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {assistantsData.map((assistant) => (
            <SelectItem value={assistant.name}>{assistant.name}</SelectItem>
          ))}
          <SelectItem value="create-assistant">Create Assistant</SelectItem>
        </SelectContent>
      </Select>
    </div>
  );
}
