'use client'
import { Button } from "@/components/ui/button";
import { AssistantSelector } from "../../build-panel/components/assistant-selector";
import { useRouter } from "next/navigation";
import { Plus } from "lucide-react";
import PersonaFlowIcon from '../../../../../assets/PersonaFlowIcon-512.png'
import Image from "next/image";

export default function Header() {
  const router = useRouter()
  return (
    <div className="flex gap-2 m-2 justify-between">
      <div className="flex gap-4 items-center">
      <Image className="rounded" src={PersonaFlowIcon} alt="PersonaFlow logo" width={40} height={40}/>
        <h1>AgentStack</h1>
        </div>
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
