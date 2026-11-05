"use client";

import React from "react";
import Link from "next/link";

interface NavbarProps {
  breadcrumbs?: Array<{ label: string; href?: string }>;
}

export default function Navbar({
  breadcrumbs = [
    { label: "Projects", href: "#" },
    { label: "Mysteries" },
  ],
}: NavbarProps) {
  return (
    <header className="h-[46px] w-full flex items-center px-5 bg-[#181818] border-b border-[#262626] select-none text-[13px] font-mono">
      <nav aria-label="Breadcrumb" className="flex items-center gap-2">
        {breadcrumbs.map((crumb, idx) => {
          const isLast = idx === breadcrumbs.length - 1;

          return (
            <React.Fragment key={`${crumb.label}-${idx}`}>
              {idx > 0 && (
                <span className="text-[#555555] font-light select-none">/</span>
              )}
              {isLast ? (
                <span className="text-[#ececec] font-medium tracking-wide">
                  {crumb.label}
                </span>
              ) : crumb.href ? (
                <Link
                  href={crumb.href}
                  className="text-[#999999] hover:text-[#e0e0e0] transition-colors"
                >
                  {crumb.label}
                </Link>
              ) : (
                <span className="text-[#999999]">{crumb.label}</span>
              )}
            </React.Fragment>
          );
        })}
      </nav>
    </header>
  );
}
