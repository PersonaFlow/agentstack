'use client'
import { getSlugParams } from '@/lib/utils';
import { useParams } from 'next/navigation';
import { useMemo } from 'react';


/**
 *
 * @description This hook is used to parse the slug from the URL and return the agentId and conversationId.
 * The slug can be in the following formats:
 * - [] - /
 * - NOT THIS [c, :conversationId] - /c/:conversationId
 * - [a, :agentId] - /a/:agentId
 * - [a, :agentId, c, :conversationId] - /a/:agentId/c/:conversationId
 */

export const useSlugRoutes = () => {
    const {params} = useParams();

  const { assistantId, threadId } = useMemo(() => {
    const slug = (params ?? []) as string[];
    return getSlugParams(slug);
  }, [params]);

  return { assistantId, threadId };
};