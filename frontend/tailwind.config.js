/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f5f7ff',
          100: '#ebf0fe',
          200: '#ced9fd',
          300: '#a3b7fc',
          400: '#718efa',
          500: '#4f6bf5',
          600: '#384de6',
          700: '#2c3bc6',
          800: '#27329f',
          900: '#242e7e',
        }
      }
    },
  },
  plugins: [],
}
