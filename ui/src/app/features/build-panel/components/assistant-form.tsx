"use client";

import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { UseFormReturn } from "react-hook-form";
import { Button } from "@/components/ui/button";
import SelectModel from "./select-model";
import { SelectLLM } from "./select-llm";
import { SystemPrompt } from "./system-prompt";
import { RetrievalInstructions } from "./retrieval-description";
import SelectTools from "./select-tools";
import SelectCapabilities from "./select-capabilities";
import SelectOptions from "./select-options";
import SelectActions from "./select-actions";
import FilesDialog from "./files-dialog";
import PublicSwitch from "./public-switch";
import SelectArchitecture from "./select-architecture";
import SelectFiles from "./select-files";
import { useRunnableConfigSchema } from "@/data-provider/query-service";
import Spinner from "@/components/ui/spinner";

type TAssistantFormProps = {
  form: UseFormReturn<any>;
  onSubmit: (arg?: any) => void;
};

export function AssistantForm({ form, onSubmit }: TAssistantFormProps) {
  const { type: architectureType } = form.getValues().config.configurable;
  const { data: config, isLoading, isError } = useRunnableConfigSchema();

  if (isLoading) return <Spinner />;

  if (isError) return <div>There was an issue fetching config schema.</div>;

  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className="overflow-y-scroll hide-scrollbar"
      >
        <div className="flex flex-col gap-6">
          <div className="flex gap-6">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormControl>
                    <Input
                      placeholder="Assistant Name"
                      type="text"
                      {...field}
                      className="w-[400px]"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <PublicSwitch form={form} />
          </div>

          <SelectArchitecture
            form={form}
            types={config?.definitions.Bot_Type.enum ?? []}
          />

          {architectureType && (
            <>
              {architectureType === "agent" ? (
                <SelectModel
                  form={form}
                  models={config?.definitions.AgentType.enum ?? []}
                />
              ) : (
                <SelectLLM
                  form={form}
                  llms={config?.definitions.LLMType.enum ?? []}
                />
              )}
              <SystemPrompt form={form} />
              {architectureType !== "chatbot" && (
                <>
                  <SelectCapabilities form={form} />
                  <RetrievalInstructions form={form} />
                  <div className="flex gap-6 flex-col">
                    <SelectFiles form={form} />
                    <div className="w-50">
                      <FilesDialog form={form} />
                    </div>
                  </div>
                  {architectureType !== "chat_retrieval" && (
                    <SelectTools form={form} />
                  )}
                  <SelectOptions form={form} />
                  {architectureType !== "chat_retrieval" && (
                    <SelectActions form={form} />
                  )}
                </>
              )}
              <Button type="submit" className="w-1/4 self-center">
                Save
              </Button>
            </>
          )}
        </div>
      </form>
    </Form>
  );
}
