"use client";

import { useState } from "react";
import { AssistantSelector } from "./AssistantSelector";
import { Button } from "@/components/ui/button";
import { TCreateAssistant } from "@/data-provider/types";
import { SquareIcon } from "@radix-ui/react-icons";
import { EditAssistant } from "./EditAssistant";
import { CreateAssistant } from "./CreateAssistant";

interface TSelectedAssistant extends TCreateAssistant {
  id?: string;
}

export function AssistentBuilder() {
  const [selectedAssistant, setSelectedAssistant] = useState<
    TSelectedAssistant | undefined
  >(undefined);

  return (
    <>
      <div className="flex gap-3">
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
        <CreateAssistant />
      )}
    </>
  );
}
