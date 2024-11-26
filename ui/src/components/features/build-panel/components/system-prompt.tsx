'use client'
import { FormControl, FormField, FormItem, FormLabel } from '@/components/ui/form'
import { Textarea } from '@/components/ui/textarea'
import { UseFormReturn } from 'react-hook-form'

type TSystemPromptProps = {
  form: UseFormReturn<any>
}

export function SystemPrompt({ form }: TSystemPromptProps) {
  return (
    <FormField
      control={form.control}
      name="config.configurable.system_message"
      render={({ field }) => (
        <FormItem className="flex flex-col">
          <FormLabel>System Prompt</FormLabel>
          <FormControl>
            <Textarea
              {...field}
              className="w-[400px]"
              placeholder="Instructions for the assistant. ex: 'You are a helpful assistant'"
            />
          </FormControl>
        </FormItem>
      )}
    />
  )
}
