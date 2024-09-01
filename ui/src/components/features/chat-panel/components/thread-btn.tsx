import { Button } from "@/components/ui/button"
import { threadAtom } from "@/store"
import { useAtom } from "jotai"

export const ThreadBtn = () => {
    const [_, setIsNavbarOpen] = useAtom(threadAtom)

    const openNavbar = () => setIsNavbarOpen(isOpen => !isOpen);

    return <Button variant="outline" className="w-1/4 m-2" onClick={openNavbar}>Threads</Button>
}