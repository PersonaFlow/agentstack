import { Badge } from "@/components/ui/badge";
import { FormControl, FormField, FormItem } from "@/components/ui/form";
import Spinner from "@/components/ui/spinner";
import { useFiles as useFilesQuery } from "@/data-provider/query-service";
import { CircleX } from "lucide-react";
import { useEffect, useState } from "react";
import { UseFormReturn, useFieldArray } from "react-hook-form";

type TSelectFilesProps = {
  form: UseFormReturn<any>;
};

type TBadgeValue = {
  label: string;
  value: string;
};

export default function SelectFiles({ form }: TSelectFilesProps) {
  const [badgeValues, setBadgeValues] = useState([]);

  const { data: files, isLoading } = useFilesQuery("assistants");

  const fileIds = form.watch("file_ids");

  const { remove } = useFieldArray({
    name: "file_ids",
    control: form.control,
  });

  useEffect(() => {
    if (files && !isLoading) {
      const _badgeValues = fileIds.map((id: string) => {
        const fileData = files?.find((file) => file.id === id);
        return { label: fileData?.filename, value: fileData?.id };
      });

      setBadgeValues(_badgeValues);
    }
  }, [fileIds, files]);

  if (isLoading) return <Spinner />;

  return (
    <div className="flex gap-2 flex-wrap">
      {badgeValues.map((badgeValue: TBadgeValue, index: number) => {
        return (
          <FormField
            key={badgeValue.value}
            control={form.control}
            name="file_ids"
            render={({ field }) => {
              return (
                <FormItem>
                  <FormControl>
                    <Badge
                      className="rounded-full flex cursor-pointer text-xs gap-2"
                      onClick={() => remove(index)}
                    >
                      <p>{badgeValue.label}</p>
                      <CircleX className="w-4" />
                    </Badge>
                  </FormControl>
                </FormItem>
              );
            }}
          />
        );
      })}
    </div>
  );
}
