"use client";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import Spinner from "@/components/ui/spinner";
import { useAssistant, useAssistants } from "@/data-provider/query-service";
import { TAssistant } from "@/data-provider/types";
import { useSlugRoutes } from "@/hooks/useSlugParams";
import { assistantAtom } from "@/store";
import { useAtom } from "jotai";
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
      console.log(assistantId)
      const _selectedAssistant = assistantsData?.find(
        (assistant) => assistant.id === assistantId,
      );

      console.log(_selectedAssistant)

      setSelectedAssistant(_selectedAssistant);
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
