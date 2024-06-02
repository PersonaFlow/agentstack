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
import { useEffect } from "react";

type TAssistantProps = {
  setSelectedAssistant: (arg: TAssistant | null) => void;
  selectedAssistant: TAssistant | null;
};

export function AssistantSelector({
  setSelectedAssistant,
  selectedAssistant,
}: TAssistantProps) {
  const { data: assistantsData, isLoading } = useAssistants();

  const handleValueChange = (value: string) => {
    const selectedAssistant = assistantsData?.find(
      (assistant) => assistant.name === value,
    );
    console.log(selectedAssistant);
    if (selectedAssistant) setSelectedAssistant(selectedAssistant);
  };

  useEffect(() => {
    if (assistantsData && !isLoading) {
      assistantsData?.length > 0
        ? setSelectedAssistant(assistantsData[0])
        : setSelectedAssistant(null);
    }
  }, []);

  if (isLoading) return <LoaderCircle />;

  return (
    <div className="px-2">
      <Select
        onValueChange={handleValueChange}
        defaultValue={
          selectedAssistant ? selectedAssistant.name : "create-assistant"
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
