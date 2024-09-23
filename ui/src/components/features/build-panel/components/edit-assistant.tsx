"use client";

import {
  useAssistant,
  useUpdateAssistant,
} from "@/data-provider/query-service";
import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect, useMemo } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { TAssistant, formSchema } from "@/data-provider/types";
import { AssistantForm } from "./assistant-form";
import { useConfigSchema } from "@/hooks/useConfig";
import { useAvailableTools } from "@/hooks/useAvailableTools";
import { useToast } from "@/components/ui/use-toast";
import { useSlugRoutes } from "@/hooks/useSlugParams";
import Spinner from "@/components/ui/spinner";

const RetrievalType = "retrieval";

export function EditAssistant() {
  const { assistantId } = useSlugRoutes();
  const { data: selectedAssistant, isLoading: isLoadingAssistant } =
    useAssistant(assistantId as string, {
      enabled: !!assistantId,
    });
  
  
  useEffect(() => {
    console.log(selectedAssistant)
  },[selectedAssistant])

  return isLoadingAssistant ? (
    <Spinner />
  ) : (
    <>
      {selectedAssistant ? (
        <EditAssistantForm selectedAssistant={selectedAssistant} />
      ) : (
        <div>Assistant not found</div>
      )}
    </>
  );
}

function EditAssistantForm({
  selectedAssistant,
}: {
  selectedAssistant: TAssistant;
}) {
  const updateAssistant = useUpdateAssistant(selectedAssistant.id as string);

  const form = useForm<TAssistant>({
    resolver: zodResolver(formSchema),
    defaultValues: useMemo(() => {
      return selectedAssistant as TAssistant;
    }, [selectedAssistant]),
  });

  const architectureType = form.watch("config.configurable.type");
  const tools = form.watch("config.configurable.tools");

  const { toast } = useToast();

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
      // @ts-ignore
      form.setValue("config.configurable.system_message", systemMessage);
      form.setValue(
        "config.configurable.retrieval_description",
        // @ts-ignore
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
        form.setValue("config.configurable.tools", [retrievalTool.toString()]);
      }
    }
  }, [architectureType]);

  function onSubmit(values: z.infer<typeof formSchema>) {
    // @ts-ignore
    updateAssistant.mutate(values, {
      onSuccess: () => {
        toast({
          variant: "default",
          title: "Successfully updated assistant.",
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
      <h1 className="text-2xl font-bold">Edit Assistant</h1>
      <AssistantForm form={form} onSubmit={onSubmit} />
    </>
  );
}
