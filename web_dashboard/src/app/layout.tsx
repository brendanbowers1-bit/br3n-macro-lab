import "@/styles/globals.css";
import type { Metadata } from "next";
import { DashboardProvider } from "@/components/DashboardProvider";
import { readDashboardSync } from "@/lib/data.server";

export const metadata: Metadata = {
  title: "BR3N Macro Lab — Research Intelligence",
  description: "Value Survival · Settlement Economics · Stablecoin Settlement Windows",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const initial = readDashboardSync();
  return (
    <html lang="en">
      <body className="font-sans antialiased">
        <DashboardProvider initial={initial}>{children}</DashboardProvider>
      </body>
    </html>
  );
}
