import { cn } from "@/lib/utils";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";

type TMarkdownProps = {
  text: string;
  className?: string;
};

export default function Markdown({ text, className }: TMarkdownProps) {
  return (
    <div
      className={cn(
        "prose max-w-none",
        "prose-p:my-4",
        "prose-ol:my-0 prose-ol:space-y-2 prose-ol:whitespace-normal",
        "prose-ul:my-0 prose-ul:space-y-2 prose-ul:whitespace-normal",
        "prose-li:my-0",
        "prose-pre prose-pre:mb-0 prose-pre:mt-0",
        "prose-code:!whitespace-pre-wrap prose-code:!bg-transparent prose-code:!p-0",
        "prose-img:my-2",
        "prose-headings:my-4",
        "prose-h1:mb-6",
        "prose-h1:font-medium prose-h2:font-medium prose-h3:font-medium prose-h4:font-medium prose-h5:font-medium prose-h6:font-medium prose-strong:font-medium",
        "prose-h1:text-xl prose-h2:text-lg prose-h3:text-base prose-h4:text-base prose-h5:text-base prose-h6:text-base",
        "prose-pre:border prose-pre:border-secondary-100 prose-pre:bg-secondary-50 prose-pre:text-volcanic-900",
        className,
      )}
    >
      <ReactMarkdown remarkPlugins={[remarkGfm, remarkMath]}>
        {text}
      </ReactMarkdown>
    </div>
  );
}
