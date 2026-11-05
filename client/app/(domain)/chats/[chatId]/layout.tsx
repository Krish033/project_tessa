import Navbar from '@/components/layouts/Navbar'
import React from 'react'

export default function layout({children}: Readonly<{children: React.ReactNode}>) {
  return (
    <>
      <Navbar />
      {children}
    </>
  )
}
