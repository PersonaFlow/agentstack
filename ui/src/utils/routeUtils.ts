export function isValidParam(params?: string[]) {
  if (!params) return true

  const route = params.join('/')

  const UUIDPattern = '[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}'
  const assistantPattern = new RegExp(`a/${UUIDPattern}$`, 'i')

  const threadPattern = new RegExp(`a/${UUIDPattern}/c/${UUIDPattern}$`, 'i')

  return assistantPattern.test(route) || threadPattern.test(route)
}

export const isUUID = (value: string) => {
  const isValidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i

  return isValidRegex.test(value)
}

// Note: If we support creating threads independent of assistants in the future, need to support /c/:threadId

/**
 *
 * @description This function is used to parse the slug from the URL and return the assistantId and threadId.
 * The slug can be in the following formats:
 * - [] - / - Home
 * - [a, :assistantId] - /a/:assistantId - Assistant is selected
 * - [a, :assistantId, c, :threadId] - /a/:assistantId/c/:threadId - Thread is selected
 */

export const getSlugParams = (
  slugParams?: string | string[],
): {
  assistantId: string | undefined
  threadId: string | undefined
} => {
  if (!slugParams || typeof slugParams === 'string') {
    return { assistantId: undefined, threadId: undefined }
  }

  const [firstParam, secondParam, thirdParam, fourthParam] = slugParams

  // Case 1: [/]
  if (!firstParam) {
    return { assistantId: undefined, threadId: undefined }
  }

  // Case 2: [/a/:assistantId]
  if (firstParam === 'a' && isUUID(secondParam) && !thirdParam) {
    return { assistantId: secondParam, threadId: undefined }
  }

  // Case 3: [/a/:assistantId/c/:threadId]
  if (firstParam === 'a' && isUUID(secondParam) && thirdParam === 'c' && isUUID(fourthParam)) {
    return { assistantId: secondParam, threadId: fourthParam }
  }

  return { assistantId: undefined, threadId: undefined }
}
