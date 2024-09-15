import { MessageType, TMessage } from "@/data-provider/types";
import Markdown from "../../markdown/markdown";

type TMessageItemProps = {
  message: TMessage;
};

export default function MessageItem({ message }: TMessageItemProps) {
  if (message.type === MessageType.HUMAN) {
    return (
      <div className="flex w-full flex-col gap-1 items-end m-2">
        <div className="relative max-w-[70%] rounded-2xl border-2 px-5">
          <Markdown text={ message.content as string} />
        </div>
      </div>
    );
  }

  if (message.type === MessageType.AI) {
    return (
      <div className="py-2 px-3 text-base md:px-4 m-auto md:px-5 lg:px-1 xl:px-5">
        <Markdown text={ message.content as string} />
      </div>
    );
  }
}
