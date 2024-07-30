"use client";

import { useUpdateAssistant as useUpdateAssistantMutation } from "@/data-provider/query-service";
import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect, useMemo } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { TAssistant, formSchema } from "@/data-provider/types";
import { AssistantForm } from "./assistant-form";
import { useConfigSchema } from "@/hooks/useConfig";
import { useAvailableTools } from "@/hooks/useAvailableTools";

const RetrievalType = "retrieval";

export function EditAssistant({ assistant }: { assistant: TAssistant }) {
  const assistantMutation = useUpdateAssistantMutation(assistant?.id as string);

  const form = useForm<TAssistant>({
    resolver: zodResolver(formSchema),
    defaultValues: useMemo(() => assistant, [assistant]),
  });

  const architectureType = form.watch("config.configurable.type");
  const tools = form.watch("config.configurable.tools");

  const { systemMessage, retrievalDescription } = useConfigSchema(
    architectureType ?? "",
  );

  const { availableTools } = useAvailableTools();

  useEffect(() => {
    if (assistant) {
      form.reset(assistant);
    }
  }, [assistant, form]);

  useEffect(() => {
    if (architectureType) {
      // @ts-ignore
      form.setValue("config.configurable.system_message", systemMessage);
      form.setValue(
        "config.configurable.retrieval_description",
        // @ts-ignore
        retrievalDescription,
      );
    }
  }, [architectureType, form, retrievalDescription, systemMessage]);

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
        form.setValue("config.configurable.tools", [retrievalTool.toString()]);
      }
    }
  }, [architectureType]);

  function onSubmit(values: z.infer<typeof formSchema>) {
    // @ts-ignore
    assistantMutation.mutate(values);
  }

  return (
    <>
      <h1>Edit Assistant</h1>
      <AssistantForm form={form} onSubmit={onSubmit} />
    </>
  );
}
