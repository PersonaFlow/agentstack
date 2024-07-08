"use client";

import {
  useAssistants,
  useCreateAssistant,
} from "@/data-provider/query-service";
import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { AssistantForm } from "./assistant-form";
import { useAtom } from "jotai";
import { assistantAtom } from "@/store";
import Spinner from "@/components/ui/spinner";
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
    multi_use: z.object({
      default: z.boolean(),
    }),
  }),
});

const formSchema = z.object({
  public: z.boolean(),
  name: z.string().min(1, { message: "Name is required" }),
  config: z.object({
    configurable: z.object({
      interrupt_before_action: z.boolean(),
      type: z.string().nullable(),
      agent_type: z.string().optional(),
      llm_type: z.string(),
      retrieval_description: z.string(),
      system_message: z.string(),
      tools: z.array(toolSchema),
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

const RetrievalType = "retrieval";

export function CreateAssistant() {
  const { data: assistantsData, isLoading } = useAssistants();
  const [_, setSelectedAssistant] = useAtom(assistantAtom);

  const createAssistant = useCreateAssistant();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: defaultValues,
  });

  const architectureType = form.watch("config.configurable.type");
  const tools = form.watch("config.configurable.tools");

  const { systemMessage, retrievalDescription, availableTools } =
    useConfigSchema(architectureType ?? "");

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
