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
import { TTool } from "@/data-provider/types";
import { useAvailableTools } from "@/hooks/useAvailableTools";
import { UseFormReturn } from "react-hook-form";

type TToolDialog = {
  form: UseFormReturn<any>;
};

export function ToolDialog({ form }: TToolDialog) {
  const { availableTools } = useAvailableTools();

  return (
    <Dialog>
      <DialogTrigger>
        <Button className="rounded-xl" type="button">
          Add tool
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Tools</DialogTitle>
          <DialogDescription>
            {availableTools?.map((tool) => (
              <FormField
                key={tool.type}
                control={form.control}
                name={`config.configurable.tools`}
                render={({ field }) => {
                  return (
                    <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                      <FormControl>
                        <Checkbox
                          checked={field.value?.some(
                            (selection: TTool) => selection.type === tool.type,
                          )}
                          onCheckedChange={(checked) => {
                            return checked
                              ? field.onChange([...field.value, tool])
                              : field.onChange(
                                  field.value?.filter(
                                    (selection: TTool) =>
                                      selection.type !== tool.type,
                                  ),
                                );
                          }}
                        />
                      </FormControl>
                      <FormLabel className="text-sm font-normal">
                        {tool.name}
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
