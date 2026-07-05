import type { RouterScrollBehavior } from 'vue-router'

// Back/forward should restore savedPosition, but list/detail pages load
// their data async: right after the navigation the page is still
// skeleton-height, so scrolling immediately would get clamped by the
// browser. Wait until the page grows tall enough to contain the target,
// give up after 3s (e.g. the restored list came back shorter than it
// was), and abandon the restore entirely if the user starts scrolling
// in the meantime — yanking the page from under them is worse than
// landing at the wrong spot.
function waitToRestore(position: { top: number; left: number }) {
  return new Promise<typeof position | Record<string, never>>((resolve) => {
    const deadline = performance.now() + 3000
    let cancelled = false
    const cancel = () => {
      cancelled = true
    }
    window.addEventListener('wheel', cancel, { passive: true, once: true })
    window.addEventListener('touchmove', cancel, { passive: true, once: true })
    const cleanup = () => {
      window.removeEventListener('wheel', cancel)
      window.removeEventListener('touchmove', cancel)
    }
    const check = () => {
      if (cancelled) {
        cleanup()
        resolve({}) // empty position = don't scroll at all
        return
      }
      const reachable = document.documentElement.scrollHeight - window.innerHeight >= position.top
      if (reachable || performance.now() > deadline) {
        if (!reachable && import.meta.env.DEV) {
          console.warn('[scrollBehavior] gave up waiting for page height; scroll will clamp')
        }
        cleanup()
        resolve(position)
        return
      }
      requestAnimationFrame(check)
    }
    check()
  })
}

// The scroll policy, extracted from the router options so it can be
// unit-tested without spinning up a router. Takes only the parts of the
// route it actually reads.
type NavLocation = { path: string; query: Record<string, unknown> }

export function resolveScroll(
  to: NavLocation,
  from: NavLocation,
  savedPosition: { left: number; top: number } | null,
) {
  if (savedPosition) {
    return waitToRestore(savedPosition)
  }
  // Same path = a query-only navigation (filters syncing to the URL),
  // not a page change — leave the scroll position alone.
  if (to.path === from.path) {
    return {}
  }
  return { top: 0 }
}

export const scrollBehavior: RouterScrollBehavior = (to, from, savedPosition) =>
  resolveScroll(to, from, savedPosition)
