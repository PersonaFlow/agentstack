'use client'

import { FormField, FormItem, FormLabel } from '@/components/ui/form'
import { Textarea } from '@/components/ui/textarea'
import { UseFormReturn } from 'react-hook-form'

type TRetrievalInstructionsProps = {
  form: UseFormReturn<any>
}

export function RetrievalInstructions({ form }: TRetrievalInstructionsProps) {
  return (
    <FormField
      control={form.control}
      name="config.configurable.retrieval_description"
      render={({ field }) => {
        return (
          <FormItem className="flex flex-col gap-2">
            <FormLabel>Retrieval Instructions</FormLabel>
            <Textarea className="h-[125px]" {...field} />
          </FormItem>
        )
      }}
    />
  )
}
