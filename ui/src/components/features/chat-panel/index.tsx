import { ChatForm } from "./components/chat-form";
import Messages from "./components/messages";

export default function ChatPanel() {
  return (
    <div className="h-full w-full gap-4 flex flex-col">
      <Messages />
      <ChatForm />
    </div>
  );
}
