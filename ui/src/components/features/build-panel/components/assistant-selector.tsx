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
import { useSlugRoutes } from "@/hooks/useSlugParams";
import { useRouter } from "next/navigation";

export function AssistantSelector() {
  const { assistantId } = useSlugRoutes();
  const { data: assistantsData, isLoading } = useAssistants();
  const router = useRouter();

  if (isLoading || !assistantsData) return <Spinner />;

  const handleValueChange = (selectedAssistantId: string) => {
    router.push(`/a/${selectedAssistantId}`);
  };
  const selectedAssistant = assistantsData.find(
    (assistant) => assistant.id === assistantId,
  );

  return (
    <Select
      onValueChange={handleValueChange}
      value={selectedAssistant?.id ?? ""}
    >
      <SelectTrigger className="w-[180px] border-accent">
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
