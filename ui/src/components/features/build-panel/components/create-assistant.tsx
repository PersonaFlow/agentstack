"use client";

import { useCreateAssistant } from "@/data-provider/query-service";
import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { AssistantForm } from "./assistant-form";
import { useConfigSchema } from "@/hooks/useConfig";
import { formSchema } from "@/data-provider/types";
import { useAvailableTools } from "@/hooks/useAvailableTools";
import { useToast } from "@/components/ui/use-toast";
import { useRouter } from "next/navigation";
import { SquarePlus } from "lucide-react";

const defaultValues = {
  public: false,
  name: "",
  config: {
    configurable: {
      interrupt_before_action: false,
      type: "",
      agent_type: "GPT 4o Mini",
      llm_type: "GPT 4o Mini",
      retrieval_description: "",
      system_message: "",
      tools: [],
    },
  },
  file_ids: [],
};

const RetrievalType = "retrieval";

export function CreateAssistant() {
  const createAssistant = useCreateAssistant();

  const router = useRouter();

  const { toast } = useToast();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues,
  });
  console.log(defaultValues);
  console.log('inside create',form.getValues())

  const architectureType = form.watch("config.configurable.type");
  const tools = form.watch("config.configurable.tools");

  // Only use config schema as defaults - don't use in edit
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
    if (architectureType && architectureType !== "agent") {
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
      // const containsCodeInterpreter = tools.includes("Code interpretor");
      // if (containsCodeInterpreter) retrievalTools.push("Code interpreter");
      form.setValue("config.configurable.tools", retrievalTools);
    }
  }, [architectureType]);

  function onSubmit(values: z.infer<typeof formSchema>) {
    // @ts-ignore
    createAssistant.mutate(values, {
      onSuccess: (response) => {
        console.log("Successfully created assistant: ");
        console.log(response);
        router.push(`/a/${response.id}`);
        toast({
          variant: "default",
          title: "Successfully created new assistant.",
        });
      },
      onError: () => {
        toast({
          variant: "destructive",
          title: "Failed to update assistant.",
        });
      },
    });
  }

  return (
    <>
      <div className="flex gap-2 items-center">
        <SquarePlus />
        <h1 className="text-2xl">Create</h1>
      </div>
      <AssistantForm form={form} onSubmit={onSubmit} />
    </>
  );
}
