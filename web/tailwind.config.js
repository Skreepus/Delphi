/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // Matches Streamlit `app.py` Delphi theme
        delphi: {
          bg: "#0d0d0d",
          surface: "#161616",
          border: "#2a2a2a",
          text: "#e8e2d9",
          muted: "#6b6560",
          accent: "#c9a96e",
          "accent-dim": "#a08b5a",
        },
      },
      fontFamily: {
        sans: ["Merriweather", "Georgia", "serif"],
        display: ["Cormorant Garamond", "Georgia", "serif"],
        mono: ["ui-monospace", "SFMono-Regular", "monospace"],
      },
    },
  },
  plugins: [],
};
