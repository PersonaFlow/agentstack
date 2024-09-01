"use client";

import { EditAssistant } from "./edit-assistant";
import { CreateAssistant } from "./create-assistant";
import { useSlugRoutes } from "@/hooks/useSlugParams";

export function AssistentBuilder() {
  const {assistantId} = useSlugRoutes();

  return (
    <>
      {assistantId ? <EditAssistant /> : <CreateAssistant />}
    </>
  );
}
