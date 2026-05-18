/**
 * Lightweight debounce function to prevent excessive API requests
 */
export function useDebounceFn(fn: (...args: any[]) => any, delay: number = 300) {
  let timeoutId: ReturnType<typeof setTimeout>
  return (...args: any[]) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn(...args), delay)
  }
}
