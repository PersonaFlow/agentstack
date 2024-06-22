import { Button } from "@/components/ui/button";
import { PlusSquareIcon } from "lucide-react";

type TNewThreadBtnProps = {
  handleClick: () => void;
};

export default function NewThreadBtn({ handleClick }: TNewThreadBtnProps) {
  return (
    <Button onClick={handleClick} className="p-6 w-[calc(100%-20px)]">
      <a className="flex gap-x-2 items-center">
        <PlusSquareIcon />
        <span>New thread</span>
      </a>
    </Button>
  );
}
