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
import Spinner from "@/components/ui/spinner";
import { useRunnableConfigSchema } from "@/data-provider/query-service";
import { TTool } from "@/data-provider/types";
import { useConfigSchema } from "@/hooks/useConfig";
import { UseFormReturn } from "react-hook-form";

type TToolDialog = {
  form: UseFormReturn<any>;
};

export function ToolDialog({ form }: TToolDialog) {
  const { data: config, isLoading, isError } = useRunnableConfigSchema();
  const { availableTools } = useConfigSchema(config);

  if (isLoading) return <Spinner />;

  if (isError) return <div>Issue fetching available tools.</div>;

  return (
    <Dialog>
      <DialogTrigger>
        <Button className="rounded-xl">Add tool</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Tools</DialogTitle>
          <DialogDescription>
            {availableTools?.map((tool) => (
              <FormField
                key={tool.id}
                control={form.control}
                name={`config.configurable.tools`}
                render={({ field }) => {
                  return (
                    <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                      <FormControl>
                        <Checkbox
                          checked={field.value?.some(
                            (selection: TTool) => selection.id === tool.id,
                          )}
                          onCheckedChange={(checked) => {
                            return checked
                              ? field.onChange([...field.value, tool])
                              : field.onChange(
                                  field.value?.filter(
                                    (selection: TTool) =>
                                      selection.id !== tool.id,
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
