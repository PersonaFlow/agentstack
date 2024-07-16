import { MessageType, TMessage } from "@/data-provider/types";
// import Markdown from "../../markdown/markdown";
import { unified } from "unified";
import remarkParse from "remark-parse";
import remarkRehype from "remark-rehype";
import rehypeDocument from "rehype-document";
import rehypeFormat from "rehype-format";
import rehypeStringify from "rehype-stringify";
import { read } from "to-vfile";
import ReactMarkdown from "react-markdown";
import Markdown from "../../markdown/markdown";

type TMessageItemProps = {
  message: TMessage;
};

// async function getFormattedText(text: string) {
//   const result = await unified()
//     .use(remarkParse)
//     .use(remarkRehype)
//     .use(rehypeDocument)
//     .use(rehypeFormat)
//     .use(rehypeStringify)
//     .process(await read(text));
//   return result;
// }

export default function MessageItem({ message }: TMessageItemProps) {
  // const content = getFormattedText(message.content);
  if (message.type === MessageType.HUMAN) {
    return (
      <div className="flex w-full flex-col gap-1 items-end">
        <div className="relative max-w-[70%] rounded-3xl border-2 px-5 py-2.5">
          <div>{message.content as string}</div>
        </div>
      </div>
    );
  }

  if (message.type === MessageType.AI) {
    return (
      <div className="py-2 px-3 text-base md:px-4 m-auto md:px-5 lg:px-1 xl:px-5">
        <p>{message.content as string}</p>
      </div>
    );
  }
}
