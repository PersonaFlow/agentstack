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
import { useParams } from "next/navigation";
import { useEffect } from "react";

export function AssistantSelector() {
  const [selectedAssistant, setSelectedAssistant] = useAtom(assistantAtom);
  const { data: assistantsData, isLoading } = useAssistants();

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

  if (isLoading || !assistantsData) return <Spinner />;

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
          <SelectItem key={assistant.id} value={assistant.id}>
            {assistant.name}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
