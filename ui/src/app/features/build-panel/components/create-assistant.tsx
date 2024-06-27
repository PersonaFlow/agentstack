"use client";

import {
  useAssistants,
  useCreateAssistant,
  useRunnableConfigSchema,
} from "@/data-provider/query-service";
import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect, useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { AssistantForm } from "./assistant-form";
import {
  TAssistant,
  TConfigSchema,
  TConfigurableSchema,
  TSchemaField,
} from "@/data-provider/types";
import { useAtom } from "jotai";
import { assistantAtom } from "@/store";
import Spinner from "@/components/ui/spinner";

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
  name: "",
  config: {
    configurable: {
      interrupt_before_action: false,
      type: "",
      agent_type: "GPT 3.5 Turbo",
      llm_type: "GPT 3.5 Turbo",
      retrieval_description: "",
      system_message: "",
      tools: [],
    },
  },
  file_ids: [],
};

const systemMessage = (
  configSchema: TConfigurableSchema,
  selectedArchType: string,
) => {
  const configProperties =
    configSchema?.definitions["Configurable" as TConfigurableSchema].properties;

  if (selectedArchType === "chat_retrieval") {
    return configProperties["type==chat_retrieval/system_message"].default;
  }

  if (selectedArchType === "chatbot") {
    return configProperties["type==chatbot/system_message"].default;
  }

  if (selectedArchType === "agent") {
    return configProperties["type==agent/system_message"].default;
  }
};

export function CreateAssistant() {
  const { data: assistantsData, isLoading } = useAssistants();
  const [_, setSelectedAssistant] = useAtom(assistantAtom);

  const createAssistant = useCreateAssistant();
  const { data: configSchema } = useRunnableConfigSchema();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: defaultValues,
  });

  const architectureType = form.watch("config.configurable.type");
  const tools = form.watch("config.configurable.tools");

  useEffect(() => {
    if (configSchema && architectureType) {
      const message = systemMessage(configSchema, architectureType);
      form.setValue("config.configurable.system_message", message);
    }
  }, [configSchema, architectureType]);

  useEffect(() => {
    if (architectureType !== "agent") {
      // Unregister agent_type
      form.unregister("config.configurable.agent_type");
    }

    if (architectureType === "chatbot") {
      form.setValue("config.configurable.tools", []);
    }

    if (architectureType === "chat_retrieval") {
      const retrievalTools = ["Retrieval"];
      const containsCodeInterpreter = tools.includes("Code interpretor");
      // if (containsCodeInterpreter) retrievalTools.push("Code interpreter");
      form.setValue("config.configurable.tools", retrievalTools);
    }
  }, [architectureType]);

  function onSubmit(values: z.infer<typeof formSchema>) {
    createAssistant.mutate(values, {
      onSuccess: (response) => {
        console.log(response);
        setSelectedAssistant(response);
      },
    });
  }

  if (isLoading || !assistantsData) return <Spinner />;

  return <AssistantForm form={form} onSubmit={onSubmit} />;
}
