"use client";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import Spinner from "@/components/ui/spinner";
import { useAssistants } from "@/data-provider/query-service";
import { TAssistant, TCreateAssistant } from "@/data-provider/types";
import { LoaderCircle } from "lucide-react";

interface TSelectedAssistant extends TCreateAssistant {
  id?: string;
}

type TAssistantProps = {
  setSelectedAssistant: (arg: TSelectedAssistant | null) => void;
  selectedAssistant?: TAssistant;
};

export function AssistantSelector({
  setSelectedAssistant,
  selectedAssistant,
}: TAssistantProps) {
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

  if (isLoading) return <Spinner />;

  return (
    <div className="px-2">
      <Select
        onValueChange={handleValueChange}
        value={selectedAssistant ? selectedAssistant.name : undefined}
      >
        <SelectTrigger className="w-[180px]">
          <SelectValue placeholder="Select assistant.." />
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
