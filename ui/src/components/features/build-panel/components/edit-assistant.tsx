"use client";

import {
  useAssistants,
  useUpdateAssistant,
} from "@/data-provider/query-service";
import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect, useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { TAssistant, formSchema } from "@/data-provider/types";
import { AssistantForm } from "./assistant-form";
import { useAtom } from "jotai";
import { assistantAtom } from "@/store";
import { useConfigSchema } from "@/hooks/useConfig";
import { useAvailableTools } from "@/hooks/useAvailableTools";

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

  const { systemMessage, retrievalDescription } = useConfigSchema(
    architectureType ?? "",
  );

  const { availableTools } = useAvailableTools();

  useEffect(() => {
    if (selectedAssistant) {
      form.reset(selectedAssistant);
    }
  }, [selectedAssistant]);

  useEffect(() => {
    if (architectureType) {
      form.setValue("config.configurable.system_message", systemMessage);
      form.setValue(
        "config.configurable.retrieval_description",
        retrievalDescription,
      );
    }
  }, [architectureType]);

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
