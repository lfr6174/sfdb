import { ref } from 'vue'

const SPOILER_KEY = 'spoiler'

// Global reactive state for the SPA.
// By keeping this ref outside the function, all components share the same state naturally.
const isSpoilerProtected = ref(localStorage.getItem(SPOILER_KEY) !== 'false')

export function useSpoiler() {
  // Local state for tracking revealed items within a specific component instance
  const revealedSpoilers = ref<Set<number>>(new Set())

  const toggleSpoiler = () => {
    isSpoilerProtected.value = !isSpoilerProtected.value
    localStorage.setItem(SPOILER_KEY, String(isSpoilerProtected.value))
  }

  const revealSpoiler = (itemId: number) => {
    revealedSpoilers.value.add(itemId)
  }

  const clearRevealedSpoilers = () => {
    revealedSpoilers.value.clear()
  }

  return { isSpoilerProtected, toggleSpoiler, revealedSpoilers, revealSpoiler, clearRevealedSpoilers }
}
