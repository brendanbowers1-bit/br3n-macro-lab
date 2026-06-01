import "@/styles/globals.css";
import type { Metadata } from "next";
import { DashboardProvider } from "@/components/DashboardProvider";
import { readDashboardSync } from "@/lib/data.server";
import { withBasePath } from "@/lib/base-path";

export const metadata: Metadata = {
  title: "BR3N Macro Lab — Bowers Frontier Institute",
  description: "Division research dashboard · Value Survival · Settlement · Stablecoin Finality",
  icons: {
    icon: [{ url: withBasePath("/assets/brand/bfi-icon.svg"), type: "image/svg+xml" }],
    apple: withBasePath("/assets/brand/bfi-icon.svg"),
  },
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
