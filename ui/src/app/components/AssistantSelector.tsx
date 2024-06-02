"use client";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useAssistants } from "@/data-provider/query-service";
import { TCreateAssistant } from "@/data-provider/types";
import { LoaderCircle } from "lucide-react";
import { useEffect } from "react";

interface TSelectedAssistant extends TCreateAssistant {
  id?: string;
}

type TAssistantProps = {
  setSelectedAssistant: (arg: TSelectedAssistant | null) => void;
};

export function AssistantSelector({ setSelectedAssistant }: TAssistantProps) {
  const { data: assistantsData, isLoading } = useAssistants();

  const handleValueChange = (assistantId: string) => {
    const _selectedAssistant = assistantsData?.find(
      (assistant) => assistant.id === assistantId,
    );

    if (_selectedAssistant) {
      delete _selectedAssistant.updated_at;
      delete _selectedAssistant.user_id;

      setSelectedAssistant(_selectedAssistant);
    }
  };

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
              <SelectItem key={assistant.id} value={assistant.id}>
                {assistant.name}
              </SelectItem>
            ))}
        </SelectContent>
      </Select>
    </div>
  );
}
