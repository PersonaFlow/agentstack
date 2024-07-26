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
import { useSlugRoutes } from "@/hooks/useSlugParams";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export function AssistantSelector() {
  const [selectedAssistant, setSelectedAssistant] = useState<TAssistant>();

  const {assistantId} = useSlugRoutes();
  const { data: assistantsData, isLoading } = useAssistants();
  const router = useRouter();

  useEffect(() => {
    if (isLoading) return;

    if (!selectedAssistant || assistantId !== selectedAssistant?.id) {
      updateSelectedAssistant(assistantId as string)
    }
  },[assistantId, assistantsData])

  const handleValueChange = (selectedAssistantId: string) => {
    router.push(`/a/${selectedAssistantId}`)

    const _selectedAssistant = assistantsData?.find(
      (assistant) => assistant.id === selectedAssistantId,
    );

    if (_selectedAssistant) {
      setSelectedAssistant(_selectedAssistant);
    }
  };

  const updateSelectedAssistant = (selectedId: string) => {
    const _selectedAssistant = assistantsData?.find(
      (assistant) => assistant.id === selectedId,
    );

    setSelectedAssistant(_selectedAssistant);
  }

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
          <SelectItem key={assistant.id} value={assistant.id as string}>
            {assistant.name}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
