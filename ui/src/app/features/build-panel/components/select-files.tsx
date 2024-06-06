"use client";

import { Checkbox } from "@/components/ui/checkbox";
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
} from "@/components/ui/form";
import { useFiles } from "@/data-provider/query-service";
import { UseFormReturn } from "react-hook-form";

type TSelectFilesProps = {
  form: UseFormReturn<any>;
};
export default function SelectFiles({ form }: TSelectFilesProps) {
  const { data: files, isLoading } = useFiles("1234");

  if (isLoading || !files) return <div>loading...</div>;

  return (
    <div className="flex flex-col gap-2 mb-3">
      <h1 className="text-lg font-semibold leading-none tracking-tight">
        Add Assistant Files
      </h1>
      {files.map((file) => (
        <FormField
          key={file.id}
          control={form.control}
          name="file_ids"
          render={({ field }) => {
            return (
              <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                <FormControl>
                  <Checkbox
                    checked={field.value?.includes(file.id)}
                    onCheckedChange={(checked) => {
                      return checked
                        ? field.onChange([...field.value, file.id])
                        : field.onChange(
                            field.value?.filter(
                              (value: string) => value !== file.id,
                            ),
                          );
                    }}
                  />
                </FormControl>
                <FormLabel className="text-sm font-normal">
                  {file.filename}
                </FormLabel>
              </FormItem>
            );
          }}
        />
      ))}
    </div>
  );
}
