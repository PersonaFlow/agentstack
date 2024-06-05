"use client";

import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { UseFormReturn } from "react-hook-form";
import { Button } from "@/components/ui/button";
import SelectModel from "./select-model";
import { SelectLLM } from "./select-llm";
import { SystemPrompt } from "./system-prompt";
import { RetrievalInstructions } from "./retrieval-description";
import SelectTools from "./select-tools";
import SelectCapabilities from "./select-capabilities";
import SelectOptions from "./select-options";
import SelectActions from "./select-actions";
import FilesDialog from "./files-dialog";

const architectureTypes = [
  { display: "Chat", value: "chatbot" },
  { display: "Chat with Retrieval", value: "chat_retrieval" },
  { display: "Agent", value: "agent" },
];

type TAssistantFormProps = {
  form: UseFormReturn<any>;
  onSubmit: (arg?: any) => void;
};

export function AssistantForm({ form, onSubmit }: TAssistantFormProps) {
  console.log(form);
  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className="overflow-y-scroll hide-scrollbar"
      >
        <div className="flex flex-col gap-6">
          <div className="flex gap-6">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormControl>
                    <Input
                      placeholder="Assistant Name"
                      type="text"
                      {...field}
                      className="w-[400px]"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="public"
              render={({ field }) => (
                <FormItem className="flex flex-col">
                  <FormLabel>Public</FormLabel>
                  <FormControl>
                    <Switch
                      onCheckedChange={(checked) => field.onChange(checked)}
                    />
                  </FormControl>
                </FormItem>
              )}
            />
          </div>

          <FormField
            control={form.control}
            name="config.configurable.type"
            render={({ field }) => (
              <FormItem className="flex flex-col">
                <FormLabel>Architecture</FormLabel>
                <FormControl>
                  <Select onValueChange={field.onChange}>
                    <SelectTrigger className="w-[180px]">
                      <SelectValue placeholder="Select architecture" />
                    </SelectTrigger>
                    <SelectContent>
                      {architectureTypes.map((item) => (
                        <SelectItem key={item.value} value={item.value}>
                          {item.display}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </FormControl>
              </FormItem>
            )}
          />
          {form.getValues().config.configurable.type && (
            <>
              {form.getValues().config.configurable.type === "agent" ? (
                <SelectModel form={form} />
              ) : (
                <SelectLLM form={form} />
              )}
              <SystemPrompt form={form} />
              {form.getValues().config.configurable.type !== "chatbot" && (
                <>
                  <SelectCapabilities form={form} />
                  <RetrievalInstructions form={form} />
                  <div className="flex my-3">
                    <FilesDialog form={form} />
                  </div>
                  {form.getValues().config.configurable.type !==
                    "chat_retrieval" && <SelectTools form={form} />}
                  <SelectOptions form={form} />
                  {form.getValues().config.configurable.type !==
                    "chat_retrieval" && <SelectActions form={form} />}
                </>
              )}
              <Button type="submit" className="w-1/4 self-center">
                Save
              </Button>
            </>
          )}
        </div>
        {/* 
          <AccordionItem value="files">
            <AccordionTrigger className="p-2">Upload Files</AccordionTrigger>
            <AccordionContent className="overflow-y-scroll p-2 gap-3 flex flex-col">
              {mockFiles.map((file) => (
                <FormField
                  key={file.id}
                  control={form.control}
                  name="file_ids"
                  render={({ field }) => {
                    return (
                      <FormItem
                        key={file.id}
                        className="flex flex-row items-start space-x-3 space-y-0"
                      >
                        <FormControl>
                          <Checkbox
                            checked={field.value?.includes(file.id)}
                            onCheckedChange={(checked) => {
                              return checked
                                ? field.onChange([...field.value, file.id])
                                : field.onChange(
                                    field.value?.filter(
                                      (value) => value !== file.id,
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
              <div className="flex my-3">
                <UploadFiles />
              </div>
            </AccordionContent>
          </AccordionItem>
        </Accordion> */}
      </form>
    </Form>
  );
}
