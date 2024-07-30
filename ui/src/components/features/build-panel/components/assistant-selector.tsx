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
import { assistantAtom } from "@/store";
import { useAtom } from "jotai";

export function AssistantSelector() {
  const [selectedAssistant, setSelectedAssistant] = useAtom(assistantAtom);
  const { data: assistantsData, isLoading, isError } = useAssistants();

  const handleValueChange = (assistantId: string) => {
    const _selectedAssistant = assistantsData?.find(
      (assistant) => assistant.id === assistantId,
    );

    if (_selectedAssistant) {
      localStorage.setItem(
        "personaflow_defaultAssistant",
        JSON.stringify(_selectedAssistant),
      );
      setSelectedAssistant(_selectedAssistant);
    }
  };

  if (isLoading) return <Spinner />;
  if (isError) return <div>Failed to load assistants</div>;
  if (!assistantsData)
    return <div>No AI assistants found. Please, create one to start</div>;

  return (
    <Select
      onValueChange={handleValueChange}
      value={selectedAssistant?.id}
      defaultValue={selectedAssistant?.name}
    >
      <SelectTrigger className="w-[180px]">
        <SelectValue placeholder="Select assistant.." />
      </SelectTrigger>
      <SelectContent>
        {assistantsData.map((assistant) => (
          <SelectItem key={assistant.id} value={assistant.id as string}>
            {assistant.name}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
