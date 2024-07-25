import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function isValidParam (params?: string[]) {
  if (!params) return true;

  const route = params.join('/');

  const UUIDPattern = '[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}';
  const assistantPattern = new RegExp(`a/${UUIDPattern}$`, 'i');

  const threadPattern = new RegExp(`a/${UUIDPattern}/c/${UUIDPattern}$`, 'i');

  return assistantPattern.test(route) || threadPattern.test(route)
}

export const isUUID = (value: string) => {
  const isValidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

  return isValidRegex.test(value);
};

/**
 *
 * @description This function is used to parse the slug from the URL and return the agentId and conversationId.
 * The slug can be in the following formats:
 * - [] - /
 * - [c, :conversationId] - /c/:conversationId
 * - [a, :agentId] - /a/:agentId
 * - [a, :agentId, c, :conversationId] - /a/:agentId/c/:conversationId
 */

export const getSlugParams = (
  slugParams?: string | string[]
): {
  assistantId: string | undefined;
  threadId: string | undefined;
} => {
  if (!slugParams || typeof slugParams === 'string') {
    return { assistantId: undefined, threadId: undefined };
  }

  // Possible values are:
  // firstQuery = [:agentId, c, a, undefined]
  // secondQuery = [c, :conversationId, undefined]
  // thirdQuery = [c, undefined]
  // fourthQuery = [:conversationId, undefined]
  const [firstQuery, secondQuery, thirdQuery, fourthQuery] = slugParams;

  // [/]
  if (!firstQuery) {
    return { assistantId: undefined, threadId: undefined };
  }

  // [/c/:conversationId]
  // if (firstQuery === 'c' && isUUID(secondQuery)) {
  //   return { agentId: undefined, conversationId: secondQuery };
  // }

  // [/a/:agentId]
  if (firstQuery === 'a' && isUUID(secondQuery) && !thirdQuery) {
    return { assistantId: secondQuery, threadId: undefined };
  }

  // [/a/:agentId/c/:conversationId]
  if (firstQuery === 'a' && isUUID(secondQuery) && thirdQuery === 'c' && isUUID(fourthQuery)) {
    return { assistantId: secondQuery, threadId: fourthQuery };
  }

  return { assistantId: undefined, threadId: undefined };
};