import { Input } from "@/components/ui/input";
import Spinner from "@/components/ui/spinner";
import { TThread } from "@/data-provider/types";
import { cn } from "@/lib/utils";
import { Brain, EditIcon, Trash } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";

type TThreadItemProps = {
  thread: TThread;
};

export default function ThreadItem({ thread }: TThreadItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedName, setEditedname] = useState(thread.name || "");
  const [isSelected, setIsSelected] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const router = useRouter();

  // const threadItemStyle = 'relative h-12 overflow-hidden flex justify-start items-center p-2'

  const handleItemClick = () => {
    if (isSelected) return;
    router.push(`/c/${thread.id}`);
  };

  const submitUpdatedName = () => {};

  const handleUpdateName = () => {};

  return (
    <a
      onClick={handleItemClick}
      className={cn(
        // isSelected ? threadItemSelected : threadItemStyle,
        isDeleting ? "fade-out" : "",
        "fade-in grid grid-cols=[auto_1fr_auto] gap-2 items-center cursor-pointer",
      )}
    >
      <Brain />
      {!isEditing ? (
        <span className="truncate">{thread.name}</span>
      ) : (
        <Input
          value={editedName}
          onChange={handleUpdateName}
          onBlur={submitUpdatedName}
          autoFocus
        />
      )}
      {/* {isFetching && <Spinner />} */}
      {isSelected && (
        <div className="flex text-white ml-auto">
          <EditIcon onClick={() => setIsEditing((prev) => !prev)} />
          <Trash />
        </div>
      )}
    </a>
  );
}
