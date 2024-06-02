"use client";

import { useState } from "react";
import { AssistantSelector } from "./AssistantSelector";
import { Button } from "@/components/ui/button";
import { TAssistant } from "@/data-provider/types";
import { SquareIcon } from "@radix-ui/react-icons";
import { EditAssistant } from "./EditAssistant";
import { CreateAssistant } from "./CreateAssistant";

export function OpenedPanel() {
  const [selectedAssistant, setSelectedAssistant] = useState<TAssistant | null>(
    null,
  );

  return (
    <>
      <div className="flex gap-3">
        <AssistantSelector
          setSelectedAssistant={setSelectedAssistant}
          selectedAssistant={selectedAssistant}
        />
        <Button
          className="flex gap-2"
          onClick={() => setSelectedAssistant(null)}
        >
          <SquareIcon />
          Create Assistant
        </Button>
      </div>
      {selectedAssistant ? (
        <EditAssistant selectedAssistant={selectedAssistant} />
      ) : (
        <CreateAssistant />
      )}
    </>
  );
}
