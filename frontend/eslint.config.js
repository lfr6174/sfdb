import pluginVue from 'eslint-plugin-vue'
import vueTsEslintConfig from '@vue/eslint-config-typescript'
import eslintPluginPrettierRecommended from 'eslint-plugin-prettier/recommended'

export default [
  // 0. Global ignore: never lint build output (mirrors .gitignore).
  //    Without this, `eslint .` also checks the minified JS in dist/ and
  //    reports hundreds of false errors.
  { ignores: ['dist/**'] },

  // 1. Vue 3 recommended rules (template parsing + baseline safety).
  ...pluginVue.configs['flat/recommended'],

  // 2. Vue's official TypeScript rules.
  ...vueTsEslintConfig(),

  {
    rules: {
      'no-unused-vars': 'off',

      '@typescript-eslint/no-unused-vars': 'warn',
      'vue/no-unused-vars': 'warn',

      '@typescript-eslint/no-explicit-any': 'warn',

      'vue/multi-word-component-names': 'off',
    },
  },

  eslintPluginPrettierRecommended,
]
