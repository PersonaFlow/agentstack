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
import { useForm } from "react-hook-form";
import { z } from "zod";
import { mockFiles } from "@/mockFiles";
import { Button } from "@/components/ui/button";
import UploadFiles from "./UploadFiles";

const formSchema = z.object({
  public: z.boolean(),
  name: z.string(),
  config: z.object({
    configurable: z.object({
      interrupt_before_action: z.boolean(),
      type: z.string(),
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

const tools = [
  "DDG Search",
  "Search (Tavily)",
  "Search (short answer, Tavily)",
  "Retrieval",
  "Arxiv",
  "PubMed",
  "Wikipedia",
];

const architectureType = [
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

  const botType = form.watch("config.configurable.type");

  useEffect(() => {
    if (botType !== "agent") {
      // Set undefined agent_type if bot is not an agent
      form.setValue("config.configurable.agent_type", undefined);
    }
  }, [botType]);

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
        <Accordion type="multiple">
          <AccordionItem value="Assistant Builder">
            <AccordionTrigger className="p-2">
              Build Assistants
            </AccordionTrigger>
            <AccordionContent className="p-2 flex flex-col gap-5 my-3">
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
              <div className="flex gap-6">
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
                            {architectureType.map((item) => (
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

                {form.getValues().config.configurable.type === "agent" && (
                  <FormField
                    control={form.control}
                    name="config.configurable.agent_type"
                    render={({ field }) => (
                      <FormItem className="flex flex-col">
                        <FormLabel>Agent Type</FormLabel>
                        <FormControl>
                          <Select
                            // value={form.getValues().config.configurable.type !== "agent" && undefined}
                            onValueChange={field.onChange}
                            defaultValue={field.value}
                          >
                            <SelectTrigger className="w-[180px]">
                              <SelectValue placeholder="Select Agent Type" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="GPT 3.5 Turbo">
                                GPT 3.5 Turbo
                              </SelectItem>
                              <SelectItem value="GPT 4 Turbo">
                                GPT 4 Turbo
                              </SelectItem>
                              <SelectItem value="GPT 4 (Azure OpenAI)">
                                GPT 4 (Azure OpenAI)
                              </SelectItem>
                              <SelectItem value="Claude 2">Claude 2</SelectItem>
                              <SelectItem value="Claude 2 (Amazon Bedrock)">
                                Claude 2 (Amazon Bedrock)
                              </SelectItem>
                              <SelectItem value="GEMINI">GEMINI</SelectItem>
                              <SelectItem value="Ollama">Ollama</SelectItem>
                            </SelectContent>
                          </Select>
                        </FormControl>
                      </FormItem>
                    )}
                  />
                )}
              </div>
              <FormField
                control={form.control}
                name="config.configurable.llm_type"
                render={({ field }) => (
                  <FormItem className="flex flex-col">
                    <FormLabel>LLM Type</FormLabel>
                    <FormControl>
                      <Select
                        onValueChange={field.onChange}
                        defaultValue={field.value}
                      >
                        <SelectTrigger className="w-[180px]">
                          <SelectValue placeholder="LLM Type" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="GPT 3.5 Turbo">
                            GPT 3.5 Turbo
                          </SelectItem>
                          <SelectItem value="GPT 4">GPT 4</SelectItem>
                          <SelectItem value="GPT 4 (Azure OpenAI)">
                            GPT 4 (Azure OpenAI)
                          </SelectItem>
                          <SelectItem value="Claude 2">Claude 2</SelectItem>
                          <SelectItem value="Claude 2 (Amazon Bedrock)">
                            Claude 2 (Amazon Bedrock)
                          </SelectItem>
                          <SelectItem value="GEMINI">GEMINI</SelectItem>
                          <SelectItem value="Ollama">Ollama</SelectItem>
                          <SelectItem value="Mixtral">Mixtral</SelectItem>
                        </SelectContent>
                      </Select>
                    </FormControl>
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="config.configurable.system_message"
                render={({ field }) => (
                  <FormItem className="flex flex-col">
                    <FormLabel>System Message</FormLabel>
                    <FormControl>
                      <Textarea
                        {...field}
                        className="w-[400px]"
                        placeholder="Instructions for the assistant. ex: 'You are a helpful assistant'"
                      />
                    </FormControl>
                  </FormItem>
                )}
              />
              <Accordion type="multiple">
                <AccordionItem value="Assistant Builder">
                  <AccordionTrigger className="p-2">Tools</AccordionTrigger>
                  <AccordionContent className="overflow-y-scroll p-2 flex flex-col gap-3">
                    {tools.map((tool) => (
                      <FormField
                        key={tool}
                        control={form.control}
                        name="config.configurable.tools"
                        render={({ field }) => {
                          return (
                            <FormItem
                              key={tool}
                              className="flex flex-row items-start space-x-3 space-y-0"
                            >
                              <FormControl>
                                <Checkbox
                                  checked={field.value?.includes(tool)}
                                  onCheckedChange={(checked) => {
                                    return checked
                                      ? field.onChange([...field.value, tool])
                                      : field.onChange(
                                          field.value?.filter(
                                            (value) => value !== tool,
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
                    <FormField
                      control={form.control}
                      name="config.configurable.interrupt_before_action"
                      render={({ field }) => {
                        return (
                          <FormItem className="flex items-center gap-2">
                            <FormLabel>Interrupt before action?</FormLabel>
                            <Switch
                              className="m-0"
                              onCheckedChange={(checked) =>
                                field.onChange(checked)
                              }
                            />
                          </FormItem>
                        );
                      }}
                    />
                  </AccordionContent>
                </AccordionItem>
              </Accordion>
              <FormField
                control={form.control}
                name="config.configurable.retrieval_description"
                render={({ field }) => {
                  return (
                    <FormItem className="flex flex-col gap-2">
                      <FormLabel>Retrieval Description</FormLabel>
                      <Textarea {...field} />
                    </FormItem>
                  );
                }}
              />
              <Button type="submit" className="w-1/4 self-center">
                Save
              </Button>
            </AccordionContent>
          </AccordionItem>

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
        </Accordion>
      </form>
    </Form>
  );
}
