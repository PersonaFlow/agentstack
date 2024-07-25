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
  const { params } = useParams();

  const { assistantId, threadId } = useMemo(() => {
    const slug = (params ?? []) as string[];
    return getSlugParams(slug);
  }, [params]);

  return { assistantId, threadId };
};
