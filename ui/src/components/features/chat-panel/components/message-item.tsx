import { TMessage } from "@/data-provider/types";
import { cn } from "@/lib/utils";

type TMessageItemProps = {
  message: TMessage;
};

export default function MessageItem({ message }: TMessageItemProps) {
  console.log(message.content);
  return (
    <div>
      <div
        className={cn(
          "group flex h-fit w-full flex-col gap-2 rounded-md p-2 text-left md:flex-row",
          "transition-colors ease-in-out",
          "hover:bg-secondary-50",
        )}
      >
        <div className="flex w-full gap-x-2">
          {/* <Avatar message={message} /> */}
          <div className="flex w-full min-w-0 max-w-message flex-1 flex-col items-center gap-x-3 md:flex-row">
            <div className="w-full">
              <div className="flex w-full flex-col justify-center gap-y-1 py-1">
                <div className="flex flex-col gap-y-1 whitespace-pre-wrap [overflow-wrap:anywhere] md:max-w-4xl">
                  {message.content}
                  {/* <MessageContent
                isLast={isLast}
                message={message}
                onRetry={onRetry}
              /> */}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
