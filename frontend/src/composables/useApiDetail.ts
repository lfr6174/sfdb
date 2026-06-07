import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { AxiosError } from 'axios'

export function useApiDetail<T>(
  fetchFn: (params: Record<string, string | string[]>) => Promise<{ data: T }>,
  options?: {
    onRefetch?: () => void
  },
) {
  const route = useRoute()
  const router = useRouter()
  const data = ref<T | null>(null)
  const isLoading = ref(true)
  const hasError = ref(false)

  const fetch = async () => {
    isLoading.value = true
    hasError.value = false
    try {
      if (options?.onRefetch) {
        options.onRefetch()
      }
      const response = await fetchFn(route.params)
      data.value = response.data
    } catch (error) {
      console.error('Failed to fetch details:', error)
      if (error instanceof AxiosError && error.response?.status === 404) {
        router.replace({
          name: 'not-found',
          params: { pathMatch: route.path.substring(1).split('/') },
        })
      } else {
        hasError.value = true
      }
    } finally {
      isLoading.value = false
    }
  }

  onMounted(fetch)

  watch(
    () => route.path,
    (newPath, oldPath) => {
      if (newPath !== oldPath) {
        fetch()
      }
    },
  )

  return { data, isLoading, hasError, refetch: fetch }
}
