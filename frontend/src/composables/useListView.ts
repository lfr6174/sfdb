import { ref, watch, onMounted, type Ref } from 'vue'
import { useDebounceFn } from './useDebounce'
import type { PaginatedResponse } from '../types'

export function useListView<T>(
  fetchFn: (
    params: Record<string, string | number | boolean>,
  ) => Promise<{ data: PaginatedResponse<T> }>,
  options?: {
    defaultOrdering?: string
    extraParams?: () => Record<string, string | number | boolean>
    initialSearch?: string
    initialPage?: number
    // External state (e.g. URL-backed refs from useUrlFilters). When given,
    // the caller owns the state and this composable only reads/writes it.
    searchQuery?: Ref<string>
    ordering?: Ref<string>
    currentPage?: Ref<number>
  },
) {
  const items = ref<T[]>([]) as import('vue').Ref<T[]>
  const isLoading = ref(false)
  const hasError = ref(false)
  const searchQuery = options?.searchQuery ?? ref(options?.initialSearch || '')
  const ordering = options?.ordering ?? ref(options?.defaultOrdering || '-created_at')
  const currentPage = options?.currentPage ?? ref(options?.initialPage || 1)
  const totalCount = ref(0)
  const totalPages = ref(1)
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
      totalPages.value = res.data.total_pages || 1
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
    if (currentPage.value !== 1) {
      currentPage.value = 1 // the page watcher below runs the fetch
    } else {
      fetch()
    }
  }, 300)

  watch([searchQuery, ordering], () => triggerFetch())
  // Refetch whenever the page changes, no matter who changed it — the
  // pagination buttons or the browser's back/forward restoring a URL.
  watch(currentPage, fetch)
  onMounted(fetch)

  const changePage = (page: number) => {
    currentPage.value = page
    window.scrollTo({ top: 0, behavior: 'smooth' })
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
