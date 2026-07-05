import { describe, expect, it } from 'vitest'
import { resolveScroll } from './scrollBehavior'

// The full navigation/scroll policy table. Every row is here on purpose:
// the three scroll fixes before this one each broke a neighbouring row
// because only the row being fixed was ever checked.
const nav = (path: string, query: Record<string, string> = {}) => ({ path, query })

describe('resolveScroll', () => {
  it('cross-page navigation lands at the top', () => {
    expect(resolveScroll(nav('/works/1'), nav('/works'), null)).toEqual({ top: 0 })
    expect(resolveScroll(nav('/works'), nav('/works/1'), null)).toEqual({ top: 0 })
  })

  it('pagination (page param changed) lands at the top', () => {
    expect(resolveScroll(nav('/persons', { page: '2' }), nav('/persons'), null)).toEqual({
      top: 0,
    })
    // Going back to page 1 removes the param entirely (1 is the default);
    // that still counts as a page change.
    expect(resolveScroll(nav('/persons'), nav('/persons', { page: '2' }), null)).toEqual({
      top: 0,
    })
  })

  it('filter tweaks (same path, page unchanged) return false — never {}: vue-router treats any truthy value as a scroll command, and that command kills in-flight smooth scrolling', () => {
    expect(resolveScroll(nav('/works', { concepts: '3' }), nav('/works'), null)).toBe(false)
    expect(
      resolveScroll(
        nav('/works', { page: '2', concepts: '3' }),
        nav('/works', { page: '2' }),
        null,
      ),
    ).toBe(false)
  })

  it('back/forward (savedPosition present) restores the position, even across pages', () => {
    const saved = { left: 0, top: 800 }
    expect(resolveScroll(nav('/persons'), nav('/persons/1'), saved)).toBeInstanceOf(Promise)
    // The page-param rule must not override a real back/forward restore.
    expect(resolveScroll(nav('/persons', { page: '2' }), nav('/persons'), saved)).toBeInstanceOf(
      Promise,
    )
  })
})
