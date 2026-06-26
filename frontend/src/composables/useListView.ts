import { ref, computed, watch, onMounted } from 'vue'
import { useDebounceFn } from './useDebounce'
import { DEFAULT_PAGE_SIZE } from '../utils/constants'

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export function useListView<T>(
  fetchFn: (
    params: Record<string, string | number | boolean>,
  ) => Promise<{ data: PaginatedResponse<T> }>,
  options?: {
    defaultOrdering?: string
    extraParams?: () => Record<string, string | number | boolean>
  },
) {
  const items = ref<T[]>([]) as import('vue').Ref<T[]>
  const isLoading = ref(false)
  const hasError = ref(false)
  const searchQuery = ref('')
  const ordering = ref(options?.defaultOrdering || '-created_at')
  const currentPage = ref(1)
  const totalCount = ref(0)
  const totalPages = computed(() => Math.max(1, Math.ceil(totalCount.value / DEFAULT_PAGE_SIZE)))
  const hasNext = ref(false)
  const hasPrev = ref(false)

  const fetch = async () => {
    isLoading.value = true
    hasError.value = false
    try {
      const params: Record<string, string | number | boolean> = {
        page: currentPage.value,
        ordering: ordering.value,
        ...(options?.extraParams?.() || {}),
      }
      if (searchQuery.value) params.search = searchQuery.value
      const res = await fetchFn(params)
      items.value = res.data.results || []
      totalCount.value = res.data.count || 0
      hasNext.value = !!res.data.next
      hasPrev.value = !!res.data.previous
    } catch (err) {
      console.error('Fetch failed:', err)
      hasError.value = true
    } finally {
      isLoading.value = false
    }
  }

  const triggerFetch = useDebounceFn(() => {
    currentPage.value = 1
    fetch()
  }, 300)

  watch([searchQuery, ordering], () => triggerFetch())
  onMounted(fetch)

  const changePage = (page: number) => {
    currentPage.value = page
    window.scrollTo({ top: 0, behavior: 'smooth' })
    fetch()
  }

  return {
    items,
    isLoading,
    hasError,
    searchQuery,
    ordering,
    currentPage,
    totalPages,
    totalCount,
    hasNext,
    hasPrev,
    changePage,
    fetch,
    triggerFetch,
  }
}
