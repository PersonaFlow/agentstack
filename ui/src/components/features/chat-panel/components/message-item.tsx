import { MessageType, TMessage } from "@/data-provider/types";

type TMessageItemProps = {
  message: TMessage;
};

export default function MessageItem({ message }: TMessageItemProps) {
  console.log(message);
  if (message.type === MessageType.HUMAN) {
    return (
      <div className="flex w-full flex-col gap-1 items-end">
        <div className="relative max-w-[70%] rounded-3xl border-2 px-5 py-2.5">
          <div>{message.content}</div>
        </div>
      </div>
    );
  }

  if (message.type === MessageType.AI) {
    return (
      <div className="py-2 px-3 text-base md:px-4 m-auto md:px-5 lg:px-1 xl:px-5">
        <p>{message.content}</p>
      </div>
    );
  }
}
