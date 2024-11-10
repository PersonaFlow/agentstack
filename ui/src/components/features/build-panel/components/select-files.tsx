import { Badge } from "@/components/ui/badge";
import { FormControl, FormField, FormItem } from "@/components/ui/form";
import Spinner from "@/components/ui/spinner";
import { useToast } from "@/components/ui/use-toast";
import { useAssistantFiles, useDeleteAssistantFile, useDeleteFile, useFiles } from "@/data-provider/query-service";
import { useSlugRoutes } from "@/hooks/useSlugParams";
import { CircleX } from "lucide-react";
import { useEffect, useState } from "react";
import { UseFormReturn, useFieldArray } from "react-hook-form";

type TBadgeValue = {
  label: string;
  value: string;
};

export default function SelectFiles() {
  const [badgeValues, setBadgeValues] = useState<TBadgeValue[]>([]);

  const deleteFile = useDeleteAssistantFile();

  const { assistantId } = useSlugRoutes();

  const {toast} = useToast();

  const { data: assistantFiles, isLoading } = useAssistantFiles(
    assistantId as string,
  );

  useEffect(() => {
    if (assistantFiles && !isLoading) {
      const _badgeValues = assistantFiles.map((assistantFile) => {
        return { label: assistantFile.filename, value: assistantFile.id };
      });
      setBadgeValues(_badgeValues);
    }
  }, [assistantFiles]);

  const handleClick = ({value: fileId}: TBadgeValue) => {

    deleteFile.mutate(
      { assistantId: assistantId as string, fileId },
      {
        onSuccess: () =>
          toast({
            variant: "default",
            title: "File has been deleted.",
          }),
      },
    );
  };

  if (isLoading) return <Spinner />;

  return (
    <div className="flex gap-2 flex-wrap">
      {badgeValues.map((badgeValue: TBadgeValue, index: number) => {
        return (
          <Badge
            key={`${index} - ${badgeValue.label}`}
            variant="outline"
            className="rounded-full flex cursor-pointer text-xs gap-1 py-1 max-w-40"
            onClick={() => handleClick(badgeValue)}
          >
            <span className="truncate">
              <p>{badgeValue.label}</p>
            </span>
            <div>
              <CircleX size={16} />
            </div>
          </Badge>
        );
      })}
    </div>
  );
}
