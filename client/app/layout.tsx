import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";
import Script from "next/script";
import QueryProvider from "@/lib/providers/QueryClientProvider";

const mononoki = localFont({
  src: [
    {
      path: "../public/fonts/mononoki-latin-400-normal.woff2",
      weight: "400",
      style: "normal",
    },
    {
      path: "../public/fonts/mononoki-latin-400-italic.woff2",
      weight: "400",
      style: "italic",
    },
    {
      path: "../public/fonts/mononoki-latin-700-normal.woff2",
      weight: "700",
      style: "normal",
    },
    {
      path: "../public/fonts/mononoki-latin-700-italic.woff2",
      weight: "700",
      style: "italic",
    },
  ],
  variable: "--font-mononoki",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Tessa Client",
  description: "Tessa Personal AI Assistant Client",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <QueryProvider>
      <html lang="en" className={`h-full antialiased ${mononoki.variable}`}>
        <body className="min-h-full flex flex-col font-mono">{children}</body>
      </html>
    </QueryProvider>
  );
}
