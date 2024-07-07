import { TConfigurableSchema } from "@/data-provider/types";

export const useConfigSchema = (
  configSchema: TConfigurableSchema,
  selectedArchType: string,
) => {
  if (!configSchema) return {};

  const { definitions } = configSchema;
  const { AvailableTools } = definitions;

  const configProperties =
    definitions["Configurable" as TConfigurableSchema].properties;

  let systemMessage = "";
  let retrievalDescription = "";

  if (selectedArchType === "chat_retrieval") {
    systemMessage =
      configProperties["type==chat_retrieval/system_message"].default;
  }

  if (selectedArchType === "chatbot") {
    systemMessage = configProperties["type==chatbot/system_message"].default;
  }

  if (selectedArchType === "agent") {
    systemMessage = configProperties["type==agent/system_message"].default;
  }

  if (selectedArchType) {
    retrievalDescription =
      configProperties["type==agent/retrieval_description"].default;
  }

  const configDefinitions = Object.entries(definitions);
  const availableTools = [];

  AvailableTools.enum.forEach((availableTool: string) => {
    // Find tool from config schema
    const toolDefinition = configDefinitions.find((definition) => {
      const { properties } = definition[1];
      if (!properties || !properties.type) return false;
      console.log(properties.type.default);
      console.log(availableTool);
      return properties.type.default === availableTool;
    });

    // Format tool to store with assistant
    const toolProperties = toolDefinition[1];

    const tool = {
      id: toolProperties.properties.type.default,
      type: toolProperties.properties.type.default,
      name: toolProperties.properties.type.name,
      description: toolProperties.properties.type.description,
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
