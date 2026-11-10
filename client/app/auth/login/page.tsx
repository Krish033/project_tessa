"use client";

import React, { useState } from "react";
import Link from "next/link";
import Image from "next/image";

export default function LoginPage() {
  const [email, setEmail] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
  };

  return (
    <div className="min-h-screen w-full bg-[#141414] text-[#ececec] font-mono flex flex-col justify-between selection:bg-[#343434] selection:text-white">
      {/* Top Header / Branding */}
      <header className="w-full px-8 py-7 md:px-12 md:py-9">
        <Link
          href="/"
          className="inline-flex items-center gap-2.5 group cursor-pointer"
        >
          {/* Claude 14-point terracotta starburst */}
          <svg
            width="22"
            height="22"
            viewBox="0 0 24 24"
            fill="none"
            className="text-[#d97757] transition-transform duration-300 group-hover:rotate-45"
          >
            <path
              d="M12 1.5v21M1.5 12h21M4.57 4.57l14.86 14.86M19.43 4.57L4.57 19.43M1.86 8.36l20.28 7.28M1.86 15.64l20.28-7.28M8.36 1.86l7.28 20.28M15.64 1.86L8.36 20.28"
              stroke="currentColor"
              strokeWidth="2.1"
              strokeLinecap="round"
            />
          </svg>
          <span className="text-[20px] tracking-tight font-medium text-[#f1ede6]">
            Claude
          </span>
        </Link>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 w-full max-w-[1380px] mx-auto px-6 md:px-12 pb-10 flex items-center">
        <div className="w-full grid grid-cols-1 lg:grid-cols-2 gap-10 lg:gap-14 items-center">
          {/* Left Column: Form & Info */}
          <div className="flex flex-col items-center lg:items-start text-center lg:text-left max-w-[430px] mx-auto lg:mx-0 w-full lg:pl-4">
            <h1 className="text-3xl md:text-[38px] font-normal tracking-tight text-[#f3f3f3] leading-tight mb-2.5">
              Question what’s next
            </h1>
            <p className="text-[13px] text-[#9a9a9a] mb-7">
              Your thinking partner for big ambitions
            </p>

            {/* Auth Box Container */}
            <div className="w-full bg-[#1b1b1b] border border-[#272727] rounded-2xl p-5 shadow-2xl flex flex-col gap-3">
              {/* Continue with Google */}
              <button
                type="button"
                className="w-full h-11 bg-[#282828] hover:bg-[#303030] active:scale-[0.99] border border-[#333333] hover:border-[#404040] rounded-xl flex items-center justify-center gap-2.5 text-[13px] font-medium text-[#f0f0f0] transition-all cursor-pointer"
              >
                {/* Official Google 4-color 'G' icon */}
                <svg width="17" height="17" viewBox="0 0 24 24">
                  <path
                    fill="#4285F4"
                    d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.66-5.17 3.66-9.17z"
                  />
                  <path
                    fill="#34A853"
                    d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.36 24 12 24z"
                  />
                  <path
                    fill="#FBBC05"
                    d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.16 0 9.97 0 12s.45 3.84 1.25 5.42l4.03-3.15z"
                  />
                  <path
                    fill="#EA4335"
                    d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.36 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"
                  />
                </svg>
                <span>Continue with Google</span>
              </button>

              {/* Continue with Apple */}
              <button
                type="button"
                className="w-full h-11 bg-[#282828] hover:bg-[#303030] active:scale-[0.99] border border-[#333333] hover:border-[#404040] rounded-xl flex items-center justify-center gap-2.5 text-[13px] font-medium text-[#f0f0f0] transition-all cursor-pointer"
              >
                {/* Official Apple icon */}
                <svg
                  width="17"
                  height="17"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                  className="text-white relative -top-[1px]"
                >
                  <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M15.97 6.37c.63-.77 1.06-1.84.94-2.92-1 .04-2.15.67-2.8 1.44-.57.66-.99 1.74-.86 2.8 1.05.08 2.09-.56 2.72-1.32" />
                </svg>
                <span>Continue with Apple</span>
              </button>

              {/* OR Divider */}
              <div className="relative my-0.5 flex items-center justify-center">
                <span className="text-[11px] text-[#737373] tracking-wider uppercase font-medium">
                  OR
                </span>
              </div>

              {/* Email Form */}
              <form onSubmit={handleSubmit} className="flex flex-col gap-3">
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email"
                  required
                  className="w-full h-11 px-3.5 bg-[#232323] border border-[#333333] focus:border-[#525252] rounded-xl text-[13px] text-[#f2f2f2] placeholder-[#6e6e6e] outline-none transition-colors"
                />

                <button
                  type="submit"
                  className="w-full h-11 bg-white hover:bg-[#ededed] active:scale-[0.99] text-[#121212] font-semibold text-[13px] rounded-xl transition-all cursor-pointer shadow-md"
                >
                  Continue with email
                </button>
              </form>
            </div>

            {/* Download desktop app button */}
            <div className="w-full flex justify-center mt-5">
              <button
                type="button"
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-[#202020] hover:bg-[#282828] border border-[#2d2d2d] hover:border-[#383838] text-[12px] text-[#a0a0a0] hover:text-[#e0e0e0] transition-colors cursor-pointer"
              >
                {/* Windows 4-pane icon */}
                <svg
                  width="13"
                  height="13"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                  className="text-[#999999]"
                >
                  <path d="M0 3.449L9.75 2.1v9.451H0m10.949-9.602L24 0v11.551H10.949M0 12.602h9.75v9.451L0 20.703m10.949-8.102H24V24l-13.051-1.951" />
                </svg>
                <span>Download desktop app</span>
              </button>
            </div>
          </div>

          {/* Right Column: Hero Photo Card */}
          <div className="w-full flex justify-center lg:justify-end">
            <div className="relative w-full max-w-[540px] aspect-[4/3] sm:aspect-[1.15/1] rounded-3xl overflow-hidden border border-[#272727] shadow-2xl bg-[#1c1c1c] group">
              <Image
                src="/login-hero.jpg"
                alt="Thinking partner workspace with notes and books"
                fill
                priority
                sizes="(max-width: 1024px) 100vw, 540px"
                className="object-cover object-center group-hover:scale-[1.01] transition-transform duration-700 ease-out"
              />

              {/* Bottom Right Floating Media Action Icon */}
              <div className="absolute bottom-4 right-4 z-10 w-8 h-8 rounded-lg bg-black/60 backdrop-blur-md border border-white/10 flex items-center justify-center text-white/80 hover:text-white hover:bg-black/80 transition-all cursor-pointer">
                {/* Play triangle inside frame */}
                <svg
                  width="13"
                  height="13"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <polygon points="6 3 20 12 6 21 6 3" />
                </svg>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Bottom spacer / aesthetic balance */}
      <footer className="w-full py-4 text-center">
        {/* Invisible or empty spacing to balance layout */}
      </footer>
    </div>
  );
}
