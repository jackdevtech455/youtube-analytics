import type { Config } from "tailwindcss";

export default {
  content: ["./app/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        yt: {
          bg: "#0f0f0f",
          surface: "#181818",
          surface2: "#202020",
          border: "#303030",
          text: "#f1f1f1",
          muted: "#aaaaaa",
          accent: "#ff0000",
        },
      },
    },
  },
  plugins: [],
} satisfies Config;
