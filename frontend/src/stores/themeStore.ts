import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const saved = localStorage.getItem('jev_theme') || 'dark'
  const currentTheme = ref<string>(saved)

  function setTheme(theme: string) {
    currentTheme.value = theme
    localStorage.setItem('jev_theme', theme)
    document.documentElement.setAttribute('data-theme', theme)
  }

  // Initialize on load
  document.documentElement.setAttribute('data-theme', currentTheme.value)

  return {
    currentTheme,
    setTheme,
  }
})
