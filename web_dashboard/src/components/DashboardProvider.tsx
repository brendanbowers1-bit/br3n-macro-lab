"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import type { DashboardPayload } from "@/lib/types";
import { loadDashboard } from "@/lib/data";

const DashboardContext = createContext<{ data: DashboardPayload | null; loading: boolean }>({
  data: null,
  loading: true,
});

export function DashboardProvider({ children, initial }: { children: ReactNode; initial?: DashboardPayload | null }) {
  const [data, setData] = useState<DashboardPayload | null>(initial ?? null);
  const [loading, setLoading] = useState(!initial);

  useEffect(() => {
    if (initial) return;
    loadDashboard().then((d) => {
      setData(d);
      setLoading(false);
    });
  }, [initial]);

  return (
    <DashboardContext.Provider value={{ data, loading }}>
      {children}
    </DashboardContext.Provider>
  );
}

export function useDashboard() {
  return useContext(DashboardContext);
}
