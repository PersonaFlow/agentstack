'use client'
import { Button } from "@/components/ui/button";
import { AssistantSelector } from "../../build-panel/components/assistant-selector";
import { useRouter } from "next/navigation";
import { Plus } from "lucide-react";

export default function Header() {
  const router = useRouter()
  return (
    <div className="flex gap-2 m-2 justify-between">
      <h1>[ personaflow ]</h1>
      <div className="flex gap-2">
       <AssistantSelector />
        <Button
          className="flex gap-2"
          onClick={() => router.push('/')}
        >
          <Plus />
          Create Assistant
        </Button>
      </div>
    </div>
  );
}
