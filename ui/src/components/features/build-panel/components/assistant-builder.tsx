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
import {
  useAssistant as useAssistantQuery,
  useThread as useThreadQuery,
} from "@/data-provider/query-service";

export function AssistentBuilder() {
  const [selectedAssistant, setSelectedAssistant] = useAtom(assistantAtom);
  const { id: threadId } = useParams<{ id: string }>();
  const { data: threadData } = useThreadQuery(threadId, {
    enabled: !!threadId,
  });
  const { data: assistantData } = useAssistantQuery(threadData?.assistant_id!, {
    enabled: !!threadData?.assistant_id,
  });

  // Select assistant when assistant data is available for current thread
  useEffect(
    function selectAssistant() {
      if (assistantData) {
        setSelectedAssistant(assistantData);
      }
    },
    [setSelectedAssistant, assistantData],
  );

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

      <hr className="border-x-8" />

      {selectedAssistant ? (
        <EditAssistant assistant={selectedAssistant} />
      ) : (
        <CreateAssistant onAssistantCreated={(a) => setSelectedAssistant(a)} />
      )}
    </>
  );
}
