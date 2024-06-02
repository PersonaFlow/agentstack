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
  //   setIsNewAssistant: (arg: boolean) => void;
};

export function AssistantSelector({
  setSelectedAssistant,
  selectedAssistant,
  //   setIsNewAssistant,
}: TAssistantProps) {
  const { data: assistantsData, isLoading } = useAssistants();

  const handleValueChange = (value: string) => {
    if (value === "create-assistant") {
      return setSelectedAssistant(null);
    }

    const _selectedAssistant = assistantsData?.find(
      (assistant) => assistant.name === value,
    );

    if (_selectedAssistant) setSelectedAssistant(_selectedAssistant);
  };

  useEffect(() => {
    if (assistantsData && !isLoading) {
      assistantsData?.length > 0
        ? setSelectedAssistant(assistantsData[0])
        : setSelectedAssistant(null);
    }
  }, [assistantsData]);

  if (isLoading) return <LoaderCircle />;

  return (
    <div className="px-2">
      <Select
        onValueChange={handleValueChange}
        defaultValue={
          assistantsData ? assistantsData[0].name : "create-assistant"
        }
      >
        <SelectTrigger className="w-[180px]">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {assistantsData &&
            assistantsData.map((assistant) => (
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
