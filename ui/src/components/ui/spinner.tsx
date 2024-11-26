import { cn } from '@/utils/utils'
import { Loader2 } from 'lucide-react'

const Spinner = ({ className }: { className?: string }) => {
  return <Loader2 className={cn('animate-spin', className)} />
}

export default Spinner
