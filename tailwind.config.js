/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        olive: {
          50: '#f5f7f0',
          100: '#e8ede0',
          200: '#d3dcc2',
          300: '#b4c49a',
          400: '#95a875',
          500: '#7a8d5a',
          600: '#5f7047',
          700: '#4d5a3a',
          800: '#404a32',
          900: '#373f2c',
        },
      },
    },
  },
  plugins: [],
}

