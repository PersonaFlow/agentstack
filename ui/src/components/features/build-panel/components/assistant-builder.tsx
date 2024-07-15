"use client";

import { AssistantSelector } from "./assistant-selector";
import { Button } from "@/components/ui/button";
import { SquareIcon } from "@radix-ui/react-icons";
import { EditAssistant } from "./edit-assistant";
import { CreateAssistant } from "./create-assistant";
import { useAtom } from "jotai";
import { assistantAtom } from "@/store";
import { useEffect } from "react";
import { useParams } from "next/navigation";
import { useAssistant, useThread } from "@/data-provider/query-service";

export function AssistentBuilder() {
  const [selectedAssistant, setSelectedAssistant] = useAtom(assistantAtom);
  const { id: threadId } = useParams<{id:string}>();

  const { data: threadData } = useThread(threadId, {
    enabled: !!threadId,
  });

  const { data: assistantData } = useAssistant(threadData?.assistant_id!, {
    enabled: !!threadData?.assistant_id,
  });

  useEffect(() => {
    if (assistantData) {
      setSelectedAssistant(assistantData);
    }
  }, [threadId, assistantData]);

  return (
    <>
      <div className="flex gap-3">
        <AssistantSelector />
        <Button
          className="flex gap-2"
          onClick={() => setSelectedAssistant(null)}
        >
          <SquareIcon />
          Create Assistant
        </Button>
      </div>
      {selectedAssistant ? <EditAssistant /> : <CreateAssistant />}
    </>
  );
}
