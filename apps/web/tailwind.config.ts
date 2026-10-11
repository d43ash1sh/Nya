import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        nya: {
          indigo: "#111D35",       // Midnight Indigo
          teal: "#5CE1D0",         // Signal Teal
          white: "#F8FAFC",        // Paper White
          slate: "#64748B",        // Supporting Slate
          accent: "#0ea5e9",       // Subtle hyperlink accent
          card: "#1e293b",
          border: "#334155",
        },
      },
      fontFamily: {
        sans: [
          "system-ui",
          "-apple-system",
          "BlinkMacSystemFont",
          "'Noto Sans Bengali'",
          "'Mukti Narrow'",
          "'SolaimanLipi'",
          "'Segoe UI'",
          "Roboto",
          "sans-serif",
        ],
        assamese: [
          "'Noto Sans Bengali'",
          "'Mukti Narrow'",
          "'SolaimanLipi'",
          "system-ui",
          "sans-serif",
        ],
      },
    },
  },
  plugins: [],
};
export default config;
