import js from '@eslint/js';
import vue from 'eslint-plugin-vue';
import unusedImports from 'eslint-plugin-unused-imports';

export default [
  js.configs.recommended,
  ...vue.configs['flat/essential'],
  {
    files: ['**/*.js', '**/*.vue'],
    ignores: [
      'src/js/**/*',
      'src/static/**/*',
      '**/node_modules/**',
    ],
    plugins: {
      'unused-imports': unusedImports,
    },
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: {
        window: 'readonly',
        document: 'readonly',
        setTimeout: 'readonly',
        clearTimeout: 'readonly',
        setInterval: 'readonly',
        clearInterval: 'readonly',
        console: 'readonly',
        alert: 'readonly',
        confirm: 'readonly',
        localStorage: 'readonly',
        Blob: 'readonly',
        URL: 'readonly',
        FileReader: 'readonly',
        CustomEvent: 'readonly',
        requestAnimationFrame: 'readonly',
        cancelAnimationFrame: 'readonly',
        navigator: 'readonly',
        FormData: 'readonly',
        File: 'readonly',
        TextDecoder: 'readonly',
        ResizeObserver: 'readonly',
        Element: 'readonly',
        AbortController: 'readonly',
        fetch: 'readonly',
        atob: 'readonly',
        self: 'readonly',
        MutationObserver: 'readonly',
      },
    },
    rules: {
      'unused-imports/no-unused-imports': 'error',
      'unused-imports/no-unused-vars': [
        'error',
        {
          vars: 'all',
          varsIgnorePattern: '^_',
          args: 'after-used',
          argsIgnorePattern: '^_',
        },
      ],
      'no-unused-vars': 'off',
    },
  },
];
