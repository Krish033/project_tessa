"use client";

import { ReactNode } from "react";
import { QueryClientProvider } from "@tanstack/react-query";
import getQueryClient from "../query-client";

// Provider component
export default function Provider({ children }: { children: ReactNode }) {
  const queryClient = getQueryClient();
  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}
