"use client";

import {
  useAssistants,
  useUpdateAssistant,
} from "@/data-provider/query-service";
import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect, useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { TAssistant } from "@/data-provider/types";
import { AssistantForm } from "./assistant-form";
import { useAtom } from "jotai";
import { assistantAtom } from "@/store";
import { useConfigSchema } from "@/hooks/useConfig";

const toolSchema = z.object({
  title: z.string(),
  properties: z.object({
    type: z.object({
      default: z.string(),
    }),
    name: z.object({
      default: z.string(),
    }),
    description: z.object({
      default: z.string(),
    }),
  }),
});

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
      tools: z.array(z.any()),
    }),
  }),
  file_ids: z.array(z.string()),
});

const RetrievalType = "retrieval";

export function EditAssistant() {
  const { data: assistantsData, isLoading } = useAssistants();
  const [selectedAssistant] = useAtom(assistantAtom);

  const updateAssistant = useUpdateAssistant(selectedAssistant?.id);

  const form = useForm<TAssistant>({
    resolver: zodResolver(formSchema),
    defaultValues: useMemo(() => {
      return selectedAssistant;
    }, [selectedAssistant]),
  });

  const architectureType = form.watch("config.configurable.type");
  const tools = form.watch("config.configurable.tools");

  const {
    formState: { errors },
  } = form;

  useEffect(() => {
    console.log(errors);
  }, [errors]);

  const { systemMessage, retrievalDescription, availableTools } =
    useConfigSchema(architectureType ?? "");

  useEffect(() => {
    if (systemMessage && retrievalDescription && architectureType) {
      form.setValue("config.configurable.system_message", systemMessage);
      form.setValue(
        "config.configurable.retrieval_description",
        retrievalDescription,
      );
    }
  }, [retrievalDescription, architectureType, systemMessage]);

  useEffect(() => {
    if (architectureType !== "agent") {
      // Set undefined agent_type if bot is not an agent
      form.setValue("config.configurable.agent_type", undefined);
    }

    if (architectureType === "chatbot") {
      form.setValue("config.configurable.tools", []);
    }

    if (architectureType === "chat_retrieval") {
      const retrievalTool = availableTools?.find(
        (tool) => tool.type === RetrievalType,
      );
      const containsCodeInterpreter = tools.includes("Code interpretor");
      // if (containsCodeInterpreter) retrievalTools.push("Code interpreter");
      if (retrievalTool) {
        form.setValue("config.configurable.tools", [retrievalTool]);
      }
    }
  }, [architectureType]);

  function onSubmit(values: z.infer<typeof formSchema>) {
    updateAssistant.mutate(values);
  }

  if (isLoading || !assistantsData) return <div>is loading</div>;

  return <AssistantForm form={form} onSubmit={onSubmit} />;
}
