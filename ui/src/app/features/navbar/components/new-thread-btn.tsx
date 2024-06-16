import { Button } from "@/components/ui/button";
import { PlusSquareIcon } from "lucide-react";

type TNewThreadBtnProps = {
  handleClick: () => void;
};

export default function NewThreadBtn({ handleClick }: TNewThreadBtnProps) {
  return (
    <Button onClick={handleClick}>
      <a className="m-auto flex h-12 cursor-pointer items-center gap-3 rounded-md border border-white/50 px-3 py-3 text-md text-white transition-colors duration-200 hover:bg-gray-500/40">
        <PlusSquareIcon />
        <span className="ml-1">New thread</span>
      </a>
    </Button>
  );
}
