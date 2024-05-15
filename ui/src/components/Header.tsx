import Link from "next/link";

const siteRoutes = [
    {href: "/", page: "Home"},
    {href: "/c/1234", page: "Chat"}
]

export default function Header() {
    return <div className="flex gap-2 justify-end">
        {
            siteRoutes.map(siteRoute => {
                return <Link href={siteRoute.href}>{siteRoute.page}</Link>
            })
        }
    </div>
}