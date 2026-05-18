/** @type {import("prettier").Config} */
export default {
  semi: false,
  singleQuote: true,
  printWidth: 100,
  singleAttributePerLine: true,
  htmlWhitespaceSensitivity: 'ignore',
  trailingComma: 'all',
  plugins: ['prettier-plugin-tailwindcss'],
}
