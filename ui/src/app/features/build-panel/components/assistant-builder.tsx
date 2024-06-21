"use client";

import { useEffect, useState } from "react";
import { AssistantSelector } from "./assistant-selector";
import { Button } from "@/components/ui/button";
import { TAssistant } from "@/data-provider/types";
import { SquareIcon } from "@radix-ui/react-icons";
import { EditAssistant } from "./edit-assistant";
import { CreateAssistant } from "./create-assistant";

export function AssistentBuilder() {
  const [selectedAssistant, setSelectedAssistant] = useState<
    TAssistant | undefined
  >(undefined);

  return (
    <>
      <div className="flex gap-3">
        {/* <AssistantSelector setSelectedAssistant={setSelectedAssistant} />
         */}
        <AssistantSelector setSelectedAssistant={setSelectedAssistant} />
        <Button
          className="flex gap-2"
          onClick={() => setSelectedAssistant(undefined)}
        >
          <SquareIcon />
          Create Assistant
        </Button>
      </div>
      {selectedAssistant ? (
        <EditAssistant selectedAssistant={selectedAssistant} />
      ) : (
        <CreateAssistant setSelectedAssistant={setSelectedAssistant} />
      )}
    </>
  );
}
