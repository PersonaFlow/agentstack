import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "@/styles/main.css";
import Header from "@/app/features/header/components/header";
import Providers from "@/providers/Providers";
import BuildPanel from "./features/build-panel/components/build-panel";
import Navbar from "./features/navbar/components/navbar";
import { Toaster } from "@/components/ui/toaster";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "PersonaFlow",
  description: "Where AI meets individuality for unmatched personalization",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <div
          className={`${inter.className} h-screen w-screen flex flex-col p-2 gap-2`}
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
  );
}
