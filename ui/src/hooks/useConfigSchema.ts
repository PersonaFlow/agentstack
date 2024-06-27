import { TConfigurableSchema } from "@/data-provider/types";

export const useConfigSchema = (
  configSchema: TConfigurableSchema,
  selectedArchType: string,
) => {
  const configProperties =
    configSchema?.definitions["Configurable" as TConfigurableSchema].properties;

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

  return {
    systemMessage,
    retrievalDescription,
  };
};
