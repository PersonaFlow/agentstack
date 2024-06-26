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
import { UseFormReturn } from "react-hook-form";

type TToolDialog = {
  form: UseFormReturn<any>;
};

export function ToolDialog({ form }: TToolDialog) {
  const { data: config, isLoading, isError } = useRunnableConfigSchema();

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
            {config?.definitions.AvailableTools.enum?.map((tool) => (
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
