/**
 * Lightweight debounce function to prevent excessive API requests
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function useDebounceFn<T extends (...args: any[]) => void>(fn: T, delay: number = 300) {
  let timeoutId: ReturnType<typeof setTimeout>
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn(...args), delay)
  }
}
