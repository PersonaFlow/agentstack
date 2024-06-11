import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "@/styles/main.css";
import Header from "@/app/features/header/components/header";
import Providers from "@/providers/Providers";
import Sidebar from "@/app/features/sidebar/components/sidebar";
import Builder from "./features/build-panel/components/build-panel";
import BuildPanel from "./features/build-panel/components/build-panel";
import { ChatForm } from "./features/conversation/components/chat-form";

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
              <Sidebar />
              <div className="border-solid border-2 w-full gap-4 flex flex-col">
                {children}
                <ChatForm />
              </div>
              <BuildPanel />
            </div>
          </Providers>
        </div>
      </body>
    </html>
  );
}
