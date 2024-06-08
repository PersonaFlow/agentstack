"use client";

import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
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
import PublicSwitch from "./public-switch";
import SelectArchitecture from "./select-architecture";

type TAssistantFormProps = {
  form: UseFormReturn<any>;
  onSubmit: (arg?: any) => void;
};

export function AssistantForm({ form, onSubmit }: TAssistantFormProps) {
  const { type: architectureType } = form.getValues().config.configurable;

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

            <PublicSwitch form={form} />
          </div>

          <SelectArchitecture form={form} />

          {architectureType && (
            <>
              {architectureType === "agent" ? (
                <SelectModel form={form} />
              ) : (
                <SelectLLM form={form} />
              )}
              <SystemPrompt form={form} />
              {architectureType !== "chatbot" && (
                <>
                  <SelectCapabilities form={form} />
                  <RetrievalInstructions form={form} />
                  <div className="flex my-3">
                    <FilesDialog form={form} />
                  </div>
                  {architectureType !== "chat_retrieval" && (
                    <SelectTools form={form} />
                  )}
                  <SelectOptions form={form} />
                  {architectureType !== "chat_retrieval" && (
                    <SelectActions form={form} />
                  )}
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