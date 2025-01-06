'use client'

import { EditAssistant } from './edit-assistant'
import { CreateAssistant } from './create-assistant'
import { useSlugRoutes } from '@/hooks/useSlugParams'

export function AssistantBuilder() {
  const { assistantId } = useSlugRoutes()

  return <>{assistantId ? <EditAssistant /> : <CreateAssistant />}</>
}
