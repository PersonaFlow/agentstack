import { useRunnableConfigSchema } from "@/data-provider/query-service";
import {
  TConfigDefinitions,
  TConfigurableSchema,
  TTool,
} from "@/data-provider/types";

export const useConfigSchema = (selectedArchType?: string) => {
  const { data: configSchema, isLoading, isError } = useRunnableConfigSchema();

  if (!configSchema || isLoading || isError) return {};

  const { definitions } = configSchema;
  const { AvailableTools } = definitions;

  const configProperties =
    definitions["Configurable" as TConfigurableSchema].properties;

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

  const configDefinitions = Object.entries(definitions);
  const availableTools: TTool[] = [];

  AvailableTools.enum.forEach((availableTool: string) => {
    // Find tool from config schema
    const toolDefinition = configDefinitions.find((definition) => {
      const { properties } = definition[1] as TConfigDefinitions;
      if (!properties || !properties.type) return false;

      return properties.type.default === availableTool;
    });

    // Format tool to store with assistant
    const toolProperties = toolDefinition[1] as TConfigDefinitions;

    const tool = {
      id: toolProperties.properties.type.default,
      type: toolProperties.properties.type.default,
      name: toolProperties.properties.name.default,
      description: toolProperties.properties.description.default,
      config: {},
    };

    availableTools.push(tool);
  });

  return {
    systemMessage,
    retrievalDescription,
    availableTools,
  };
};
