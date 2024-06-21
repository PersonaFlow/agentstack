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
import { TAssistant } from "@/data-provider/types";

type TAssistantProps = {
  setSelectedAssistant: (arg: TAssistant | null) => void;
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
      setSelectedAssistant(_selectedAssistant);
    }
  };

  if (isLoading || !assistantsData) return <Spinner />;

  return (
    <Select
      key={selectedAssistant?.name}
      onValueChange={handleValueChange}
      value={selectedAssistant?.name}
      defaultValue={selectedAssistant?.name}
    >
      <SelectTrigger className="w-[180px]">
        <SelectValue placeholder="Select assistant.." />
      </SelectTrigger>
      <SelectContent>
        {assistantsData.map((assistant) => (
          <SelectItem key={assistant.id} value={assistant.id}>
            {assistant.name}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
