import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "@/styles/main.css";
import Header from "@/components/Header";
import Providers from "@/providers/providers";


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
      <body className={`${inter.className} h-screen w-screen p-6`}>
        <Header />
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
