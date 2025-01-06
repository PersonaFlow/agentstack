'use client'
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion'
import { Checkbox } from '@/components/ui/checkbox'
import { FormControl, FormField, FormItem, FormLabel } from '@/components/ui/form'
import { TTool } from '@/data-provider/types'
import { useAvailableTools } from '@/hooks/useAvailableTools'
import { UseFormReturn } from 'react-hook-form'

type TSelectCapabilitiesProps = {
  form: UseFormReturn<any>
}

const options = [
  'retrieval',
  // { display: "Code interpretor", value: "Code interpretor" },
]

export default function SelectCapabilities({ form }: TSelectCapabilitiesProps) {
  const { availableTools } = useAvailableTools()
  const { type: architectureType } = form.getValues().config.configurable

  const capabilities = availableTools?.filter((tool) => options.includes(tool.type))

  const isChatRetrieval = (checkboxValue: string) =>
    architectureType === 'chat_retrieval' && checkboxValue === 'retrieval'

  return (
    <Accordion type="multiple">
      <AccordionItem value="Assistant Builder">
        <AccordionTrigger className="p-2">Capabilities</AccordionTrigger>
        <AccordionContent className="overflow-y-scroll p-2 flex flex-col gap-3">
          {capabilities?.map((capability) => (
            <FormField
              key={capability.type}
              control={form.control}
              name="config.configurable.tools"
              render={({ field }) => {
                return (
                  <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                    <FormControl>
                      <Checkbox
                        disabled={isChatRetrieval(capability.type)}
                        checked={
                          field.value?.some((selection: TTool) => selection.type === capability.type) ||
                          isChatRetrieval(capability.type)
                        }
                        onCheckedChange={(checked) => {
                          return checked
                            ? field.onChange([...field.value, capability])
                            : field.onChange(
                                field.value?.filter((selection: TTool) => selection.type !== capability.type),
                              )
                        }}
                      />
                    </FormControl>
                    <FormLabel className="text-sm font-normal">{capability.name}</FormLabel>
                  </FormItem>
                )
              }}
            />
          ))}
        </AccordionContent>
      </AccordionItem>
    </Accordion>
  )
}
