"use client";

import {
  useAssistants,
  useUpdateAssistant,
} from "@/data-provider/query-service";
import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect, useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { TAssistant, TConfigurableTool } from "@/data-provider/types";
import { AssistantForm } from "./build/AssistantForm";

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

  const architectureType = form.watch("config.configurable.type");
  form.watch("config.configurable.tools");

  useEffect(() => {
    if (architectureType !== "agent") {
      // Set undefined agent_type if bot is not an agent
      form.setValue("config.configurable.agent_type", undefined);
    }

    if (architectureType === "chatbot") {
      form.setValue("config.configurable.tools", []);
    }

    if (architectureType === "chat_retrieval") {
      const retrievalTools: TConfigurableTool[] = ["Retrieval"];
      const containsCodeInterpreter = form
        .getValues()
        .config.configurable.tools.includes("Code interpretor");
      if (containsCodeInterpreter) retrievalTools.push("Code interpreter");
      form.setValue("config.configurable.tools", retrievalTools);
    }
  }, [architectureType]);

  function onSubmit(values: z.infer<typeof formSchema>) {
    console.log(values);
    updateAssistant.mutate(values);
  }

  if (isLoading || !assistantsData) return <div>is loading</div>;

  return <AssistantForm form={form} onSubmit={onSubmit} />;
}
