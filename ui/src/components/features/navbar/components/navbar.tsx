'use client'
import Spinner from '@/components/ui/spinner'
import { useGetMyThreads } from '@/data-provider/query-service'
import { useEffect, useState } from 'react'
import ThreadItem from './thread-item'
import { TGroupedThreads } from '@/data-provider/types'
import { useSlugRoutes } from '@/hooks/useSlugParams'
import NewThreadBtn from './new-thread-btn'
import { useRouter } from 'next/navigation'

export default function Navbar() {
  const { data: threadsData, isLoading: threadsLoading, isFetching } = useGetMyThreads(true)

  const [filteredThreads, setFilteredThreads] = useState(threadsData || {})

  const router = useRouter()

  const { assistantId, threadId: currentThreadId } = useSlugRoutes()

  useEffect(() => {
    if (assistantId && threadsData) {
      let _filteredThreads = assistantId ? filterThreads(threadsData as TGroupedThreads) : threadsData
      setFilteredThreads(_filteredThreads)
    }
  }, [assistantId, threadsData])

  const filterThreads = (groupedThreads: TGroupedThreads) =>
    Object.entries(groupedThreads).reduce((newGroupedThreads, [grouping, threads]) => {
      const filtered = threads.filter((thread) => thread.assistant_id === assistantId)
      // @ts-ignore
      newGroupedThreads[grouping] = filtered
      return newGroupedThreads
    }, {})

  const onNewThreadClick = () => {
    router.push(`/a/${assistantId}`)
  }

  return (
    <div className="flex">
      <div className="flex h-full rounded flex-col items-center bg-transparent">
        {!threadsLoading && <NewThreadBtn handleClick={onNewThreadClick} disabled={!currentThreadId} />}
        {!threadsLoading && Object.values(filteredThreads).every((value) => value.length === 0) && (
          <div className="flex flex-col items-center justify-center w-64">
            <h1>No threads found.</h1>
          </div>
        )}
        <nav className="overflow-y-auto">
          {/* Threads loading */}
          {threadsLoading ? (
            <div className="flex flex-col items-center justify-center h-full w-64">
              <Spinner />
              <p className="mt-3">Loading threads... </p>
            </div>
          ) : (
            Object.entries(filteredThreads).map(([groupName, threads]) => {
              // @ts-ignore
              if (threads && threads.length > 0) {
                return (
                  <div key={groupName} className="w-64">
                    <h2 className="m-3 text-gray-400">{groupName}</h2>
                    {/* @ts-ignore */}
                    {threads?.map((thread) => (
                      <ThreadItem
                        key={`chat-${thread.id}`}
                        thread={thread}
                        currentThreadId={currentThreadId}
                      />
                    ))}
                  </div>
                )
              }
              return false
            })
          )}
        </nav>
      </div>
      <div className="h-5 w-[1px] bg-black rounded self-center"></div>
    </div>
  )
}
