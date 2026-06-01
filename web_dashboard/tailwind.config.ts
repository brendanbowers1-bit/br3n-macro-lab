import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        background: "#050608",
        surface: "#0B0F14",
        surfaceAlt: "#111827",
        border: "#1F2937",
        textPrimary: "#F8FAFC",
        textSecondary: "#94A3B8",
        accentGold: "#D4AF37",
        accentCyan: "#38BDF8",
        riskRed: "#EF4444",
        warningAmber: "#F59E0B",
        successGreen: "#22C55E",
        mutedPurple: "#8B5CF6",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
      },
      backdropBlur: {
        glass: "12px",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
