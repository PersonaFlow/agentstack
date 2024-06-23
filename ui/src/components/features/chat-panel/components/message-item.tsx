import { MessageType, TMessage } from "@/data-provider/types";

type TMessageItemProps = {
  message: TMessage;
};

export default function MessageItem({ message }: TMessageItemProps) {
  if (message.type === MessageType.HUMAN) {
    return (
      <div className="flex w-full flex-col gap-1 items-end">
        <div className="relative max-w-[70%] rounded-3xl border-2 px-5 py-2.5">
          <div>{message.content}</div>
        </div>
      </div>
    );
  }
  return (
    <div className="py-2 px-3 text-base md:px-4 m-auto md:px-5 lg:px-1 xl:px-5">
      <div className="group/conversation-turn relative flex w-full min-w-0 flex-col agent-turn">
        <div className="flex-col gap-1 md:gap-3">
          <div className="min-h-[20px] text-message flex flex-col items-start whitespace-pre-wrap break-words [.text-message+&]:mt-5 juice:w-full juice:items-end overflow-x-auto gap-2">
            <div className="markdown prose w-full break-words dark:prose-invert dark">
              <p>{message.content}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
