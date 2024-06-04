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
  useAssistant,
  useAssistants,
  useUpdateAssistant,
} from "@/data-provider/query-service";
import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect, useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import UploadFiles from "./FilesDialog";
import { TAssistant, TCreateAssistant } from "@/data-provider/types";
import SelectModel from "./build/SelectModel";
import { SelectLLM } from "./build/SelectLLM";
import { SystemMessage } from "./build/SystemMessage";
import SelectCapabilities from "./build/SelectCapabilities";
import { RetrievalInstructions } from "./build/RetrievalDescription";
import SelectTools from "./build/SelectTools";
import PublicSwitch from "./build/PublicSwitch";

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

const tools = [
  "DDG Search",
  "Search (Tavily)",
  "Search (short answer, Tavily)",
  "Retrieval",
  "Arxiv",
  "PubMed",
  "Wikipedia",
];

const architectureTypes = [
  { display: "Chat", value: "chatbot" },
  { display: "Chat with Retrieval", value: "chat_retrieval" },
  { display: "Agent", value: "agent" },
];

type TEditAssistantProps = {
  selectedAssistant: TAssistant;
};

export function EditAssistant({ selectedAssistant }: TEditAssistantProps) {
  const { data: assistantsData, isLoading } = useAssistants();

  const updateAssistant = useUpdateAssistant(selectedAssistant.id);

  const form = useForm<TAssistant>({
    resolver: zodResolver(formSchema),
    defaultValues: useMemo(() => {
      return selectedAssistant;
    }, [selectedAssistant]),
  });

  useEffect(() => {
    form.reset(selectedAssistant);
  }, [selectedAssistant]);

  const botType = form.watch("config.configurable.type");

  useEffect(() => {
    if (botType !== "agent") {
      // Set undefined agent_type if bot is not an agent
      form.setValue("config.configurable.agent_type", undefined);
    }
  }, [botType]);

  function onSubmit(values: TAssistant) {
    console.log(values);
    updateAssistant.mutate(values);
    // createAssistant.mutate(values);
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

            <PublicSwitch form={form} />
          </div>

          <FormField
            control={form.control}
            name="config.configurable.type"
            render={({ field }) => (
              <FormItem className="flex flex-col">
                <FormLabel>Architecture</FormLabel>
                <FormControl>
                  <Select
                    onValueChange={field.onChange}
                    defaultValue={field.value}
                  >
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
              <SystemMessage form={form} />
              {form.getValues().config.configurable.type !== "chatbot" && (
                <>
                  <SelectCapabilities form={form} />
                  <RetrievalInstructions form={form} />
                </>
              )}
              <SelectTools form={form} />
              <Button type="submit" className="w-1/4 self-center">
                Upload
              </Button>
            </>
          )}
        </div>
      </form>
    </Form>
  );
}
