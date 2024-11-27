import { Input } from '@/components/ui/input'
import { useToast } from '@/components/ui/use-toast'
import { useDeleteThread, useUpdateThread } from '@/data-provider/query-service'
import { TThread } from '@/data-provider/types'
import { useSlugRoutes } from '@/hooks/useSlugParams'
import { cn } from '@/utils/utils'
import { EditIcon, Trash } from 'lucide-react'
import { usePathname, useRouter } from 'next/navigation'
import { ChangeEvent, useEffect, useState } from 'react'

type TThreadItemProps = {
  thread: TThread
  currentThreadId: string | undefined
}

export default function ThreadItem({ thread, currentThreadId }: TThreadItemProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [editedName, setEditedname] = useState(thread.name || 'New thread')
  const [isDeleting, setIsDeleting] = useState(false)
  const [isHovering, setIsHovering] = useState(false)

  const { mutate: updateThread, variables: optimisticThread, isPending } = useUpdateThread(thread.id!)
  const deleteThread = useDeleteThread(thread.id!)

  const router = useRouter()
  const { toast } = useToast()
  const { assistantId } = useSlugRoutes()
  const isCurrentThread = currentThreadId && currentThreadId === thread.id

  const handleItemClick = () => {
    if (isCurrentThread) return
    router.push(`/a/${thread.assistant_id}/c/${thread.id}`)
  }

  const submitUpdatedName = () => {
    updateThread(
      {
        assistant_id: thread.assistant_id!,
        name: editedName,
      },
      {
        onSuccess: () =>
          toast({
            title: 'Thread has been updated.',
          }),
      },
    )
    setIsEditing((prev) => !prev)
  }

  const handleUpdateName = (e: ChangeEvent<HTMLInputElement>) => {
    setEditedname(e.target.value)
  }

  const handleDeleteThread = () => {
    setIsDeleting(true)
    deleteThread.mutate(undefined, {
      onSuccess: () => {
        router.push(`/a/${assistantId}`)
        toast({
          title: 'Thread has been deleted.',
        })
      },
    })
  }

  const handleEditing = () => {
    if (isEditing) return
    setIsEditing((prev) => !prev)
  }

  const iconStyles = 'cursor-pointer transition-all duration-200 stroke-1 hover:stroke-2 text-slate-400'

  return (
    <a
      onClick={handleItemClick}
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={() => setIsHovering(false)}
      className={cn(
        isDeleting ? 'fade-out' : '',
        isEditing || isCurrentThread ? 'bg-black' : '',
        'fade-in flex p-3 gap-2 rounded items-center cursor-pointer transition-all duration-200 hover:bg-black',
      )}
    >
      {!isEditing ? (
        <span className="truncate">{isPending ? optimisticThread.name : thread.name ?? 'New thread'}</span>
      ) : (
        <Input
          className="bg-transparent text-md p-0 m-0 h-full"
          value={editedName}
          onChange={handleUpdateName}
          onBlur={submitUpdatedName}
          autoFocus
        />
      )}
      <div className={cn(isHovering || isEditing ? 'flex ml-auto gap-2 items-center' : 'hidden')}>
        <EditIcon onClick={handleEditing} className={cn(iconStyles, isEditing && 'stroke-2')} />
        <Trash className={iconStyles} onClick={handleDeleteThread} />
      </div>
    </a>
  )
}
