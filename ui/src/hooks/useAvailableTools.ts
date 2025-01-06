import { useRunnableConfigSchema } from '@/data-provider/query-service'
import { TConfigDefinitions, TSchemaField, TTool } from '@/data-provider/types'

export const useAvailableTools = () => {
  const { data: configSchema, isLoading, isError } = useRunnableConfigSchema()

  if (!configSchema || isLoading || isError) return {}

  const { definitions } = configSchema

  const { AvailableTools } = definitions

  const configDefinitions = Object.entries(definitions)
  const availableTools: TTool[] = []

  // @ts-ignore to be able to build
  AvailableTools.enum.forEach((availableTool: string) => {
    // Find tool from config schema
    const toolDefinition = configDefinitions.find((definition) => {
      // @ts-ignore to be able to build
      const { properties } = definition[1] as TConfigDefinitions
      if (!properties || !properties.type) return false

      return properties.type.default === availableTool
    })

    // Format tool to store with assistant
    // @ts-ignore to be able to build
    const toolProperties = toolDefinition[1] as TConfigDefinitions

    const tool = {
      type: toolProperties.properties.type.default,
      name: toolProperties.properties.name.default,
      description: toolProperties.properties.description.default,
      multi_use: toolProperties.properties.multi_use.default,
      config: {},
    }

    availableTools.push(tool)
  })

  return {
    availableTools,
  }
}
