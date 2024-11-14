import { TAssistant, TMessage } from "@/data-provider/types";
import { Bot, UserRound } from "lucide-react";
import Markdown from "../../markdown/markdown";
import { forwardRef } from "react";

export const HumanMessage = ({ messageText }: { messageText: string }) => {
  return (
    <div className="flex w-full m-4 mr-0 justify-end ml-auto fade-in">
      <div className="bg-sky-100 rounded flex items-center mr-2 p-2">
        <Markdown text={messageText} />
      </div>
      <div>
        <div className="rounded-full p-2 bg-slate-300">
          <UserRound size="22" />
        </div>
      </div>
    </div>
    // <div className="flex w-full flex-col gap-1 items-end m-2">
    //   <div className="relative max-w-[70%] rounded-2xl border-2 px-5">
    //     <Markdown text={ message.content as string} />
    //   </div>
    // </div>
  );
};

export const AssistantMessage = ({
  messageText,
  assisstant,
}: {
  messageText: string;
  assisstant: TAssistant;
}) => {
  return (
    <div className="assistant-message flex flex-col items-start fade-in">
      <div className="flex gap-2 items-center">
        <div className="rounded-full p-2 bg-slate-300 content-center flex justify-center">
          <Bot size="22" />
        </div>
        <p className="text-sm text-slate-600 font-semibold">
          {assisstant.name}
        </p>
      </div>
      <div className="flex flex-col ml-12 mt-2 space-y-3 max-w-2xl">
        <div className="bg-white rounded flex-col items-center p-3 space-y-3">
          <Markdown text={messageText} />
        </div>
        {/* {isMostRecent && messageCompleted && <AssistantFooter message={message} />} */}
      </div>
    </div>
    // <div className="py-2 px-3 text-base md:px-4 m-auto md:px-5 lg:px-1 xl:px-5">
    //   <Markdown text={ message.content as string} />
    // </div>
  );
};
