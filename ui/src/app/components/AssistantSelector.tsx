"use client";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useAssistants } from "@/data-provider/query-service";
import { TAssistant } from "@/data-provider/types";
import { LoaderCircle } from "lucide-react";

type TAssistantProps = {
  setSelectedAssistant: (arg: TAssistant) => void;
};

export function AssistantSelector({ setSelectedAssistant }: TAssistantProps) {
  const { data: assistantsData, isLoading } = useAssistants();

  const handleValueChange = (value: string) => {
    const selectedAssistant = assistantsData?.find(
      (assistant) => assistant.name === value,
    );
    console.log(selectedAssistant);
    if (selectedAssistant) setSelectedAssistant(selectedAssistant);
  };

  if (!assistantsData || isLoading) return <LoaderCircle />;
  return (
    <div className="px-2">
      <Select
        onValueChange={handleValueChange}
        defaultValue={
          assistantsData.length > 0
            ? assistantsData[0].name
            : "Create Assistant"
        }
      >
        <SelectTrigger className="w-[180px]">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {assistantsData.map((assistant) => (
            <SelectItem key={assistant.id} value={assistant.name}>
              {assistant.name}
            </SelectItem>
          ))}
          <SelectItem value="create-assistant">Create Assistant</SelectItem>
        </SelectContent>
      </Select>
    </div>
  );
}
