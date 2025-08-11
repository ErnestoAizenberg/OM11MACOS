module.exports = {
  content: ["./app/templates/**/*.html"],
  theme: {
    extend: {
      colors: {
        macos: {
          'window': '1E1E1E',
          'sitebar': '252525',
          'accent': '0066CC',
        },
      },
    },
  },
  plugins: [],
  daisyui: {
    themes: ["night", "light"],
    logs: false,
  },
}
