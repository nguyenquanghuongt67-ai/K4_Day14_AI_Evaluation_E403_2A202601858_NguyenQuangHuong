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
        slate: {
          750: '#293548',
          850: '#151e2e',
          900: '#0F172A',
          800: '#1E293B',
          700: '#334155'
        },
        teal: {
          500: '#14B8A6',
          600: '#0D9488'
        }
      }
    },
  },
  plugins: [],
}
