"use client";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
} from "@/components/ui/form";
import { UseFormReturn, useFieldArray } from "react-hook-form";

type TSelectFilesProps = {
  form: UseFormReturn<any>;
};

export function FileDialog({ form }: TSelectFilesProps) {
  const { remove } = useFieldArray({
    name: "config.configurable.tools",
    control: form.control,
  });

  const { config } = form.getValues();

  return (
    <Dialog>
      <DialogTrigger>
        <Button className="rounded-xl">Add tool</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Tools</DialogTitle>
          <DialogDescription>
            {config.file_ids.map((file_id) => (
              <FormField
                key={tool}
                control={form.control}
                name={`config.configurable.tools`}
                render={({ field }) => {
                  return (
                    <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                      <FormControl>
                        <Checkbox
                          checked={field.value?.includes(tool)}
                          onCheckedChange={(checked) => {
                            return checked
                              ? field.onChange([...field.value, tool])
                              : field.onChange(
                                  field.value?.filter(
                                    (value: string) => value !== tool,
                                  ),
                                );
                          }}
                        />
                      </FormControl>
                      <FormLabel className="text-sm font-normal">
                        {tool}
                      </FormLabel>
                    </FormItem>
                  );
                }}
              />
            ))}
          </DialogDescription>
        </DialogHeader>
      </DialogContent>
    </Dialog>
  );
}
