import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import '@/styles/main.css'
import Providers from '@/providers/Providers'
import { Toaster } from '@/components/ui/toaster'
import BuildPanel from '@/components/features/build-panel/components/build-panel'
import Navbar from '@/components/features/navbar/components/navbar'
import Header from '@/components/features/header/components/header'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'PersonaFlow',
  description: 'Where AI meets individuality for unmatched personalization',
  icons: {
    icon: '/icon.ico',
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body>
        <div
          className={`${inter.className} h-screen w-screen flex flex-col p-2 gap-2 bg-background text-white`}
        >
          <Providers>
            <Header />
            <div className="flex flex-1 gap-2 overflow-y-hidden">
              <Navbar />
              {children}
              <BuildPanel />
            </div>
            <Toaster />
          </Providers>
        </div>
      </body>
    </html>
  )
}
