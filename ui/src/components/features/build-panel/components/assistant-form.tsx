'use client'

import { Form, FormControl, FormField, FormItem, FormMessage } from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { UseFormReturn } from 'react-hook-form'
import { Button } from '@/components/ui/button'
import { SystemPrompt } from './system-prompt'
import { RetrievalInstructions } from './retrieval-description'
import SelectTools from './select-tools'
import SelectCapabilities from './select-capabilities'
import SelectOptions from './select-options'
import SelectActions from './select-actions'
import PublicSwitch from './public-switch'
import { useRunnableConfigSchema } from '@/data-provider/query-service'
import type { TSchemaField } from '@/data-provider/types'
import Spinner from '@/components/ui/spinner'
import { FormSelect } from './form-select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { File, Wrench } from 'lucide-react'
import { useSlugRoutes } from '@/hooks/useSlugParams'
import FileBuilder from './file-builder'

type TAssistantFormProps = {
  form: UseFormReturn<any>
  onSubmit: (arg?: any) => void
}

export function AssistantForm({ form, onSubmit }: TAssistantFormProps) {
  const { type: architectureType } = form.getValues().config.configurable
  const { data: config, isLoading, isError } = useRunnableConfigSchema()

  const { assistantId } = useSlugRoutes()

  const {
    formState: { isDirty },
    getValues,
  } = form

  if (isLoading) return <Spinner />

  if (isError) return <div>There was an issue fetching config schema.</div>

  return (
    <>
      <Tabs defaultValue="builder-tab">
        <TabsList>
          <TabsTrigger value="builder-tab" className="gap-2">
            Assistant Builder <Wrench size={16} />
          </TabsTrigger>
          <TabsTrigger
            value="files-tab"
            className="gap-2"
            disabled={architectureType === 'chatbot' || !assistantId}
          >
            File Ingestion <File size={16} />
          </TabsTrigger>
        </TabsList>
        <TabsContent value="builder-tab">
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="overflow-y-scroll hide-scrollbar">
              <div className="rounded-md bg-gray-50 p-4 md:p-6">
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
                  </div>
                  <div className="flex gap-6">
                    <PublicSwitch form={form} />
                  </div>
                  <FormSelect
                    form={form}
                    options={(config?.definitions.Bot_Type as TSchemaField).enum ?? []}
                    formName="config.configurable.type"
                    title="Architecture"
                    placeholder="Architecture"
                  />
                  {architectureType && (
                    <>
                      {architectureType === 'agent' ? (
                        <FormSelect
                          form={form}
                          options={(config?.definitions.AgentType as TSchemaField).enum ?? []}
                          formName="config.configurable.agent_type"
                          title="Agent type"
                          placeholder="Select agent type"
                        />
                      ) : (
                        <FormSelect
                          form={form}
                          options={(config?.definitions.LLMType as TSchemaField).enum ?? []}
                          formName="config.configurable.llm_type"
                          title="LLM type"
                          placeholder="Select LLM type"
                        />
                      )}
                      <SystemPrompt form={form} />
                      {architectureType !== 'chatbot' && (
                        <>
                          <SelectCapabilities form={form} />
                          <RetrievalInstructions form={form} />
                          {architectureType !== 'chat_retrieval' && <SelectTools form={form} />}
                          <SelectOptions form={form} />
                          {architectureType !== 'chat_retrieval' && <SelectActions form={form} />}
                        </>
                      )}
                      <Button
                        variant="outline"
                        type="submit"
                        className="w-1/4 self-center"
                        disabled={!isDirty}
                      >
                        Save
                      </Button>
                    </>
                  )}
                </div>
              </div>
            </form>
          </Form>
        </TabsContent>
        <TabsContent value="files-tab">
          <FileBuilder />
        </TabsContent>
      </Tabs>
    </>
  )
}
