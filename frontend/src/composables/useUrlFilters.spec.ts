import { describe, expect, it, vi } from 'vitest'
import { defineComponent, h } from 'vue'
import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import { useUrlFilters, type FilterSpec } from './useUrlFilters'

// Mount a throwaway component that calls useUrlFilters against a real
// in-memory router, so the flush loop exercises the same async
// router.replace behavior as in the browser.
async function setup<S extends Record<string, FilterSpec>>(schema: S) {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/:pathMatch(.*)*', component: { render: () => null } }],
  })
  let filters!: ReturnType<typeof useUrlFilters<S>>
  const Host = defineComponent({
    setup() {
      filters = useUrlFilters(schema)
      return () => h('div')
    },
  })
  await router.push('/list')
  await router.isReady()
  mount(Host, { global: { plugins: [router] } })
  return { router, filters }
}

const query = (router: Awaited<ReturnType<typeof setup>>['router']) =>
  router.currentRoute.value.query

describe('useUrlFilters', () => {
  // Prevents: writes in the same tick racing each other — each starting from
  // a stale route.query and clobbering the other's param
  it('batches same-tick writes into a single navigation', async () => {
    const { router, filters } = await setup({
      genre: { type: 'csv' },
      page: { type: 'number', default: 1 },
    })
    const replace = vi.spyOn(router, 'replace')

    filters.values.genre.value = ['novel']
    filters.values.page.value = 3

    await vi.waitFor(() => expect(query(router)).toEqual({ genre: 'novel', page: '3' }))
    expect(replace).toHaveBeenCalledTimes(1)
  })

  // Prevents: watchers observing a phantom flip back to the old value during
  // the async gap between a write and the navigation landing
  it('reads reflect a write immediately, before the URL catches up', async () => {
    const { router, filters } = await setup({ search: { type: 'string' } })

    filters.values.search.value = 'solaris'

    expect(filters.values.search.value).toBe('solaris')
    expect(query(router).search).toBeUndefined() // navigation not flushed yet
  })

  // Prevents: default values polluting the URL (?page=1&ordering=name on a
  // pristine page) and breaking "URL is clean at rest"
  it('removes params again when set back to their default', async () => {
    const { router, filters } = await setup({ page: { type: 'number', default: 1 } })

    filters.values.page.value = 3
    await vi.waitFor(() => expect(query(router).page).toBe('3'))

    filters.values.page.value = 1
    await vi.waitFor(() => expect(query(router).page).toBeUndefined())
  })

  // Prevents: csv serialization drift — arrays must round-trip through the
  // URL string unchanged
  it('round-trips csv values through the URL', async () => {
    const { router, filters } = await setup({ genre: { type: 'csv' } })

    filters.values.genre.value = ['sf', 'fantasy']

    await vi.waitFor(() => expect(query(router).genre).toBe('sf,fantasy'))
    expect(filters.values.genre.value).toEqual(['sf', 'fantasy'])
  })

  // Prevents: clear() wiping params it was not asked to clear
  it('clear() resets only the given keys, all keys when omitted', async () => {
    const { router, filters } = await setup({
      search: { type: 'string' },
      genre: { type: 'csv' },
    })
    filters.values.search.value = 'x'
    filters.values.genre.value = ['sf']
    await vi.waitFor(() => expect(query(router)).toEqual({ search: 'x', genre: 'sf' }))

    filters.clear('genre')
    await vi.waitFor(() => expect(query(router)).toEqual({ search: 'x' }))

    filters.clear()
    await vi.waitFor(() => expect(query(router)).toEqual({}))
  })

  // Prevents: api:false params or untouched defaults leaking into API requests
  it('toParams() sends only active non-default filters marked for the API', async () => {
    const { router, filters } = await setup({
      search: { type: 'string', api: false },
      ordering: { type: 'string', default: 'name', api: false },
      genre: { type: 'csv' },
    })
    filters.values.search.value = 'x'
    filters.values.genre.value = ['sf']
    await vi.waitFor(() => expect(query(router).genre).toBe('sf'))

    expect(filters.toParams()).toEqual({ genre: 'sf' })
  })
})
