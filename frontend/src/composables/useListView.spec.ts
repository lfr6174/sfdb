import { afterEach, describe, expect, it, vi } from 'vitest'
import { defineComponent, h } from 'vue'
import { flushPromises, mount } from '@vue/test-utils'
import { useListView } from './useListView'
import type { PaginatedResponse } from '../types'

type Item = { id: number }

const page = (overrides: Partial<PaginatedResponse<Item>> = {}) => ({
  data: {
    count: 42,
    next: null,
    previous: null,
    total_pages: 3,
    results: [{ id: 1 }],
    ...overrides,
  },
})

// Mount a throwaway component so useListView gets the component context its
// onMounted/watch calls need.
function mountListView(
  fetchFn: Parameters<typeof useListView<Item>>[0],
  options?: Parameters<typeof useListView<Item>>[1],
) {
  let lv!: ReturnType<typeof useListView<Item>>
  const Host = defineComponent({
    setup() {
      lv = useListView<Item>(fetchFn, options)
      return () => h('div')
    },
  })
  mount(Host)
  return lv
}

afterEach(() => {
  vi.useRealTimers()
})

describe('useListView', () => {
  // Prevents: API response shape drift breaking the list contract
  // (items, count and total_pages all come from the response)
  it('loads the first page on mount and reads total_pages from the response', async () => {
    const fetchFn = vi.fn(async () => page())
    const lv = mountListView(fetchFn)
    await flushPromises()

    expect(fetchFn).toHaveBeenCalledWith(expect.objectContaining({ page: 1 }))
    expect(lv.items.value).toEqual([{ id: 1 }])
    expect(lv.totalCount.value).toBe(42)
    expect(lv.totalPages.value).toBe(3)
    expect(lv.isLoading.value).toBe(false)
  })

  // Prevents: a backend not sending total_pages (version skew) crashing the
  // pager — it must degrade to a single page, not NaN/undefined
  it('falls back to one page when total_pages is missing', async () => {
    const fetchFn = vi.fn(async () => page({ total_pages: undefined as unknown as number }))
    const lv = mountListView(fetchFn)
    await flushPromises()

    expect(lv.totalPages.value).toBe(1)
  })

  // Prevents: a failed request leaving the view stuck in loading state
  // instead of showing the error state
  it('flags the error state and stops loading when the API fails', async () => {
    const fetchFn = vi.fn(async () => {
      throw new Error('boom')
    })
    const lv = mountListView(fetchFn)
    await flushPromises()

    expect(lv.hasError.value).toBe(true)
    expect(lv.isLoading.value).toBe(false)
    expect(lv.items.value).toEqual([])
  })

  // Prevents: a new search keeping the old page number and showing page 5
  // of results that only have one page
  it('debounces search changes and resets to page one', async () => {
    vi.useFakeTimers()
    const fetchFn = vi.fn(async () => page())
    const lv = mountListView(fetchFn)
    await flushPromises()

    lv.currentPage.value = 3
    await flushPromises()
    expect(fetchFn).toHaveBeenLastCalledWith(expect.objectContaining({ page: 3 }))

    lv.searchQuery.value = 'solaris'
    await vi.advanceTimersByTimeAsync(300) // debounce window
    await flushPromises()

    expect(lv.currentPage.value).toBe(1)
    expect(fetchFn).toHaveBeenLastCalledWith(
      expect.objectContaining({ page: 1, search: 'solaris' }),
    )
  })
})
