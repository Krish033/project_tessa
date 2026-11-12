import Navbar from '@/components/layouts/Navbar'
import React from 'react'

export default function ChatIdLayout({children}: Readonly<{children: React.ReactNode}>) {
  return (
    <div className="flex-1 flex flex-col min-h-0 h-full overflow-hidden">
      <Navbar />
      <div className="flex-1 flex flex-col min-h-0 overflow-hidden relative">
        {children}
      </div>
    </div>
  )
}
