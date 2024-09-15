import { Button } from "@/components/ui/button";
import { PlusSquareIcon } from "lucide-react";

type TNewThreadBtnProps = {
  handleClick: () => void;
  disabled?: boolean;
};

export default function NewThreadBtn({ handleClick, disabled }: TNewThreadBtnProps) {
  return (
    <Button variant="outline" onClick={handleClick} className="p-6 w-[calc(100%-20px)] text-black" disabled={disabled}>
      <a className="flex gap-x-2 items-center">
        <PlusSquareIcon />
        <span>New thread</span>
      </a>
    </Button>
  );
}
