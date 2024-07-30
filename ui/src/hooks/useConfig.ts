import { useRunnableConfigSchema as useRunnableConfigSchemaQuery } from "@/data-provider/query-service";
import { TConfigurableSchema } from "@/data-provider/types";

export const useConfigSchema = (selectedArchType?: string) => {
  const {
    data: configSchema,
    isLoading,
    isError,
  } = useRunnableConfigSchemaQuery();

  if (!configSchema || isLoading || isError) return {};

  const { definitions } = configSchema;

  if ("Configurable" in definitions === false) return {};

  if ("properties" in definitions["Configurable"] === false) return {};

  const configProperties = definitions["Configurable"].properties;

  let systemMessage;
  let retrievalDescription;

  if (selectedArchType === "chat_retrieval") {
    systemMessage =
      configProperties["type==chat_retrieval/system_message"].default;
    retrievalDescription =
      configProperties["type==agent/retrieval_description"].default;
  }

  if (selectedArchType === "chatbot") {
    systemMessage = configProperties["type==chatbot/system_message"].default;
  }

  if (selectedArchType === "agent") {
    systemMessage = configProperties["type==agent/system_message"].default;
    retrievalDescription =
      configProperties["type==agent/retrieval_description"].default;
  }

  return {
    systemMessage,
    retrievalDescription,
  };
};
