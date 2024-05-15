'use client'

import { QueryClient, QueryClientProvider, HydrationBoundary } from '@tanstack/react-query'
import { ReactNode } from 'react'


function createQueryClient() {
    return new QueryClient({
      defaultOptions: {
        queries: {
          staleTime: 60 * 1000,
        },
      },
    })
  }

let browserQueryClient: QueryClient | undefined = undefined

function getQueryClient() {
    if (typeof window === 'undefined') {
        return createQueryClient()
    }

    if (!browserQueryClient) browserQueryClient = createQueryClient()
    return browserQueryClient
}

export default function Providers({children}: {children: ReactNode}) {
   const queryClient = getQueryClient()

    return <QueryClientProvider client={queryClient}>
        {/* Might have to redeclare in each server component. */}
        <HydrationBoundary>
        {children}
        </HydrationBoundary>
    </QueryClientProvider>
}