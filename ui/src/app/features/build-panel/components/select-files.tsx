import { Badge } from "@/components/ui/badge";
import { FormControl, FormField, FormItem } from "@/components/ui/form";
import { file } from "@/data-provider/endpoints";
import { useFiles } from "@/data-provider/query-service";
import { CircleX } from "lucide-react";
import { useEffect, useState } from "react";
import { UseFormReturn } from "react-hook-form";

type TSelectFilesProps = {
  form: UseFormReturn<any>;
};

type TBadgeValue = {
  label: string;
  value: string;
};

export default function SelectFiles({ form }: TSelectFilesProps) {
  const [badgeValues, setBadgeValues] = useState([]);

  const { data: files } = useFiles("1234");

  const fileIds = form.watch("file_ids");

  useEffect(() => {
    const _badgeValues = fileIds.map((id: string) => {
      const fileData = files?.find((file) => file.id === id);
      return { label: fileData?.filename, value: fileData?.id };
    });
    console.log("ids changed");
    setBadgeValues(_badgeValues);
  }, [fileIds]);

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
                      //   onClick={() => remove(index)}
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
