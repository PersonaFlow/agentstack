import { Button } from "@/components/ui/button";
import { PlusSquareIcon } from "lucide-react";

type TNewThreadBtnProps = {
  handleClick: () => void;
};

export default function NewThreadBtn({ handleClick }: TNewThreadBtnProps) {
  return (
    <Button onClick={handleClick}>
      <a>
        <PlusSquareIcon />
        <span>New thread</span>
      </a>
    </Button>
  );
}
