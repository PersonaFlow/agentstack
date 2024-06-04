"use client";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Checkbox } from "@/components/ui/checkbox";
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
import { Textarea } from "@/components/ui/textarea";
import {
  useAssistants,
  useCreateAssistant,
} from "@/data-provider/query-service";
import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect, useMemo, useState } from "react";
import { useFieldArray, useForm } from "react-hook-form";
import { z } from "zod";
import { mockFiles } from "@/mockFiles";
import { Button } from "@/components/ui/button";
import UploadFiles from "./FilesDialog";
import SelectModel from "./build/SelectModel";
import { SelectLLM } from "./build/SelectLLM";
import {
  SelectSystemMessage,
  SystemMessage,
  SystemPrompt,
} from "./build/SystemPrompt";
import {
  RetrievalDescription,
  RetrievalInstructions,
  SelectRetrievalDescription,
} from "./build/RetrievalDescription";
import SelectTools from "./build/SelectTools";
import SelectCapabilities from "./build/SelectCapabilities";
import FilesDialog from "./FilesDialog";
import SelectOptions from "./build/SelectOptions";
import SelectActions from "./build/SelectActions";

const formSchema = z.object({
  public: z.boolean(),
  name: z.string(),
  config: z.object({
    configurable: z.object({
      interrupt_before_action: z.boolean(),
      type: z.string().nullable(),
      agent_type: z.string().optional(),
      llm_type: z.string(),
      retrieval_description: z.string(),
      system_message: z.string(),
      tools: z.array(z.string()),
    }),
  }),
  file_ids: z.array(z.string()),
});

const defaultValues = {
  public: false,
  name: undefined,
  config: {
    configurable: {
      interrupt_before_action: false,
      type: null,
      agent_type: "GPT 3.5 Turbo",
      llm_type: "GPT 3.5 Turbo",
      retrieval_description:
        "Can be used to look up information that was uploaded for this assistant.",
      system_message: "You are a helpful assistant.",
      tools: [],
    },
  },
  file_ids: [],
};

const architectureTypes = [
  { display: "Chat", value: "chatbot" },
  { display: "Chat with Retrieval", value: "chat_retrieval" },
  { display: "Agent", value: "agent" },
];

export function CreateAssistant() {
  const { data: assistantsData, isLoading } = useAssistants();

  const createAssistant = useCreateAssistant();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: defaultValues,
  });

  const architectureType = form.watch("config.configurable.type");
  form.watch("config.configurable.tools");

  useEffect(() => {
    if (architectureType !== "agent") {
      // Set undefined agent_type if bot is not an agent
      form.setValue("config.configurable.agent_type", undefined);
    }
  }, [architectureType]);

  function onSubmit(values: z.infer<typeof formSchema>) {
    createAssistant.mutate(values);
  }

  if (isLoading || !assistantsData) return <div>is loading</div>;

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
                        <SelectItem value={item.value}>
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
                  <SelectTools form={form} />
                  <SelectOptions form={form} />
                  <div className="flex my-3">
                    <FilesDialog form={form} />
                  </div>
                  <SelectActions form={form} />
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
