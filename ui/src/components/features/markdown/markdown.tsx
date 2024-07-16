import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

type TMarkdownProps = {
  text: string;
};

export default function Markdown({ text }: TMarkdownProps) {
  return <ReactMarkdown remarkPlugins={[remarkGfm]}>{text}</ReactMarkdown>;
}
