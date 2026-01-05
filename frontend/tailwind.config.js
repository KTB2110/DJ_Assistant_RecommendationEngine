/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        spotify: {
          black: '#121212',
          darkgray: '#181818',
          gray: '#282828',
          lightgray: '#B3B3B3',
          white: '#FFFFFF',
          green: '#1DB954',
        }
      }
    },
  },
  plugins: [],
}