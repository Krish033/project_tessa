import type { Metadata } from "next";
import "./globals.css";

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
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col font-mono">{children}</body>
    </html>
  );
}
