import { Input } from "@/components/ui/input";
import Spinner from "@/components/ui/spinner";
import { useToast } from "@/components/ui/use-toast";
import {
  useDeleteThread,
  useUpdateThread,
} from "@/data-provider/query-service";
import { TThread } from "@/data-provider/types";
import { cn } from "@/lib/utils";
import { Brain, EditIcon, Trash } from "lucide-react";
import { usePathname, useRouter } from "next/navigation";
import { ChangeEvent, ChangeEventHandler, useEffect, useState } from "react";

type TThreadItemProps = {
  thread: TThread;
};

export default function ThreadItem({ thread }: TThreadItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedName, setEditedname] = useState(thread.name || "New thread");
  const [isSelected, setIsSelected] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const updateThread = useUpdateThread(thread.id);
  const deleteThread = useDeleteThread(thread.id);

  const router = useRouter();
  const pathname = usePathname();
  const { toast } = useToast();

  useEffect(() => {
    setIsSelected(pathname.includes(thread.id));
  }, [pathname, thread.id]);

  const handleItemClick = () => {
    if (isSelected) return;
    router.push(`/c/${thread.id}`);
  };

  const submitUpdatedName = () => {
    updateThread.mutate({
      assistant_id: thread.assistant_id,
      name: editedName,
    });
    setIsEditing((prev) => !prev);
  };

  const handleUpdateName = (e: ChangeEvent<HTMLInputElement>) => {
    setEditedname(e.target.value);
  };

  const handleDeleteThread = () => {
    setIsDeleting(true);
    deleteThread.mutate({
      onSuccess: () =>
        toast({
          title: "Successfully deleted thread",
        }),
    });
  };

  return (
    <a
      onClick={handleItemClick}
      className={cn(
        // isSelected ? threadItemSelected : threadItemStyle,
        isDeleting ? "fade-out" : "",
        "fade-in flex m-3 gap-2 items-center cursor-pointer",
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

      <div className="flex ml-auto gap-2">
        <EditIcon
          onClick={() => setIsEditing((prev) => !prev)}
          className="cursor-pointer"
        />
        <Trash className="cursor-pointer" onClick={handleDeleteThread} />
      </div>
    </a>
  );
}
