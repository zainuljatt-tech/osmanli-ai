import type { Metadata } from "next";
import { Inter, Playfair_Display } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/layout/providers";

const inter = Inter({ subsets: ["latin"] });
const playfair = Playfair_Display({ subsets: ["latin"], variable: "--font-playfair" });

export const metadata: Metadata = {
  title: "Osmanlı Yapay Zeka | Akıllı Asistanınız",
  description: "Osmanlı zarafetinde, yapay zeka gücünde. Size hizmet etmekten şeref duyarız.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="tr" suppressHydrationWarning>
      <body className={`${inter.className} ${playfair.variable}`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
