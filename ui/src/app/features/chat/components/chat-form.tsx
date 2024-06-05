import { Input } from "@/components/ui/input";
import { Send } from "lucide-react";

export function ChatForm() {
  return (
    <div className="mt-auto flex items-center m-3">
      <Input endIcon={Send} />
    </div>
  );
}
