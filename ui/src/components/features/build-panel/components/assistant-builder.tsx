"use client";

import { AssistantSelector } from "./assistant-selector";
import { Button } from "@/components/ui/button";
import { SquareIcon } from "@radix-ui/react-icons";
import { EditAssistant } from "./edit-assistant";
import { CreateAssistant } from "./create-assistant";
import { useAtom } from "jotai";
import { assistantAtom } from "@/store";

export function AssistentBuilder() {
  const [selectedAssistant, setSelectedAssistant] = useAtom(assistantAtom);

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
