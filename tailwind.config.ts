import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        serif: ['Crimson Pro', 'serif'],
      },
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        primary: '#374151',
        secondary: '#F8FAFC',
        accent: '#6B7280',
        neutral: '#E5E7EB',
      },
    },
  },
  plugins: [],
};
export default config;
