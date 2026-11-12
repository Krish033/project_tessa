import Navbar from "@/components/layouts/Navbar";
import Sidebar from "@/components/layouts/Sidebar";
import React, { Suspense } from "react";

export default function DomainLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#202020]">
      <Suspense fallback={<aside className="w-75 px-3 h-screen bg-[#2a2929] border-r border-[#383838]" />}>
        <Sidebar />
      </Suspense>
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <main className="flex-1 flex flex-col min-h-0 overflow-hidden">{children}</main>
      </div>
    </div>
  );
}
