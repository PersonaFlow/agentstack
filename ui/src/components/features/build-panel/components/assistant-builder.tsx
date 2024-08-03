"use client";

import { AssistantSelector } from "./assistant-selector";
import { Button } from "@/components/ui/button";
import { SquareIcon } from "@radix-ui/react-icons";
import { EditAssistant } from "./edit-assistant";
import { CreateAssistant } from "./create-assistant";
import { useRouter } from "next/navigation";
import { useSlugRoutes } from "@/hooks/useSlugParams";

export function AssistentBuilder() {
  const {assistantId} = useSlugRoutes();
  const router = useRouter()

  return (
    <>
      <div className="flex gap-3">
        <AssistantSelector />
        <Button
          className="flex gap-2"
          onClick={() => router.push('/')}
        >
          <SquareIcon />
          Create Assistant
        </Button>
      </div>
      {assistantId ? <EditAssistant /> : <CreateAssistant />}
    </>
  );
}
