"use client";

import { useCreateAssistant as useCreateAssistantMutation } from "@/data-provider/query-service";
import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { AssistantForm } from "./assistant-form";
import { useConfigSchema } from "@/hooks/useConfig";
import { formSchema, TAssistant } from "@/data-provider/types";
import { useAvailableTools } from "@/hooks/useAvailableTools";

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

const RetrievalType = "retrieval";

export function CreateAssistant({
  onAssistantCreated,
}: {
  onAssistantCreated: (a: TAssistant) => void;
}) {
  const createAssistantMutation = useCreateAssistantMutation();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: defaultValues,
  });

  const architectureType = form.watch("config.configurable.type");
  const tools = form.watch("config.configurable.tools");

  const { systemMessage, retrievalDescription } = useConfigSchema(
    architectureType ?? "",
  );

  const { availableTools } = useAvailableTools();

  useEffect(() => {
    if (architectureType) {
      form.setValue(
        "config.configurable.system_message",
        systemMessage as string,
      );
      form.setValue(
        "config.configurable.retrieval_description",
        retrievalDescription,
      );
    }
  }, [architectureType]);

  useEffect(() => {
    if (architectureType !== "agent") {
      // Unregister agent_type
      form.unregister("config.configurable.agent_type");
    }

    if (architectureType === "chatbot") {
      form.setValue("config.configurable.tools", []);
    }

    if (architectureType === "chat_retrieval") {
      const retrievalTool = availableTools?.find(
        (tool) => tool.type === RetrievalType,
      );
      const retrievalTools = [retrievalTool];
      const containsCodeInterpreter = tools.includes("Code interpretor");
      // if (containsCodeInterpreter) retrievalTools.push("Code interpreter");
      form.setValue("config.configurable.tools", retrievalTools);
    }
  }, [architectureType]);

  function onSubmit(values: z.infer<typeof formSchema>) {
    // @ts-ignore
    createAssistantMutation.mutate(values, {
      onSuccess: (response) => {
        console.log("Successfully created assistant: ");
        console.log(response);
        onAssistantCreated(response);
      },
    });
  }

  return (
    <>
      <h1>Create Assistant</h1>
      <AssistantForm form={form} onSubmit={onSubmit} />
    </>
  );
}
