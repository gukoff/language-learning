module.exports = {
  env: {
    browser: true,
    es2020: true,
    jest: true
  },
  extends: [
    "eslint:recommended"
  ],
  parserOptions: {
    ecmaVersion: 2020,
    sourceType: "module"
  },
  rules: {
    "no-unused-vars": "error",
    "no-console": "warn",
    "prefer-const": "error",
    "no-var": "error",
    "eqeqeq": "error",
    "complexity": ["error", 15],
    "max-lines-per-function": ["error", 50]
  }
};