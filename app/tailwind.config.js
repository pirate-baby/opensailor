/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./webapp/templates/**/*.html",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#217399',
        accent: '#4CA6CF',
        secondary: '#A7D3E8',
        white: '#FFFFFF',
      },
      fontFamily: {
        script: ['Rouge Script', 'cursive'],
      },
    }
  },
  plugins: [],
}