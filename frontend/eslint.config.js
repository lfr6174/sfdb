import pluginVue from 'eslint-plugin-vue'
import vueTsEslintConfig from '@vue/eslint-config-typescript'
import eslintPluginPrettierRecommended from 'eslint-plugin-prettier/recommended'

export default [
  // 1. Vue 3 官方推薦規則 (包含範本解析與基礎防呆)
  ...pluginVue.configs['flat/recommended'],

  // 2. Vue 官方的 TypeScript 規則
  ...vueTsEslintConfig(),

  {
    rules: {
      'no-unused-vars': 'off',

      '@typescript-eslint/no-unused-vars': 'warn',
      'vue/no-unused-vars': 'warn',

      '@typescript-eslint/no-explicit-any': 'off',

      'vue/multi-word-component-names': 'off'
    }
  },

  eslintPluginPrettierRecommended
]
