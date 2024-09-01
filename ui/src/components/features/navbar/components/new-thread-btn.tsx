import { Button } from "@/components/ui/button";
import { PlusSquareIcon } from "lucide-react";

type TNewThreadBtnProps = {
  handleClick: () => void;
  disabled?: boolean;
};

export default function NewThreadBtn({ handleClick, disabled }: TNewThreadBtnProps) {
  return (
    <Button onClick={handleClick} className="p-6 w-[calc(100%-20px)]" disabled={disabled}>
      <a className="flex gap-x-2 items-center">
        <PlusSquareIcon />
        <span>New thread</span>
      </a>
    </Button>
  );
}
