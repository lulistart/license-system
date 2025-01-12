import DefaultTheme from 'vitepress/theme'
import { h } from 'vue'

export default {
  ...DefaultTheme,
  Layout: () => {
    return h(DefaultTheme.Layout)
  }
}