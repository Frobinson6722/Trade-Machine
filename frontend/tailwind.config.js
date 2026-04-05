/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        profit: '#22c55e',
        loss: '#ef4444',
        accent: '#3b82f6',
      },
    },
  },
  plugins: [],
}
