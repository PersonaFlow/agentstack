"use client";
import { getSlugParams } from "@/utils/routeUtils";
import { useParams } from "next/navigation";
import { useMemo } from "react";

/**
 *
 * @description This hook parses the current route and returns assistantId and threadId.
 * The slug can be in the following formats:
 * - [] - /
 * - [a, :assistantId] - /a/:assistantId
 * - [a, :assistantId, c, :threadId] - /a/:assistantId/c/:threadId
 */

export const useSlugRoutes = () => {
  const {slug} = useParams();

  const { assistantId, threadId } = useMemo(() => {
    const formatSlug = (slug ?? []) as string[];
    return getSlugParams(formatSlug);
  }, [slug]);

  return { assistantId, threadId };
};
