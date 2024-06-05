"use client";

import {
  useAssistants,
  useCreateAssistant,
} from "@/data-provider/query-service";
import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { AssistantForm } from "./build/AssistantForm";

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

    if (architectureType === "chatbot") {
      form.setValue("config.configurable.tools", []);
    }

    if (architectureType === "chat_retrieval") {
      const retrievalTools = ["Retrieval"];
      const containsCodeInterpreter = form
        .getValues()
        .config.configurable.tools.includes("Code interpretor");
      if (containsCodeInterpreter) retrievalTools.push("Code interpreter");
      form.setValue("config.configurable.tools", retrievalTools);
    }
  }, [architectureType]);

  function onSubmit(values: z.infer<typeof formSchema>) {
    console.log(values);
    createAssistant.mutate(values);
  }

  if (isLoading || !assistantsData) return <div>is loading</div>;

  return <AssistantForm form={form} onSubmit={onSubmit} />;
}
