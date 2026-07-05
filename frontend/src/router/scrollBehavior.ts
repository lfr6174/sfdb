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
  return new Promise<typeof position | false>((resolve) => {
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
        resolve(false) // don't scroll at all
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
  // Same path = a query-only navigation (list state syncing to the URL).
  // Pagination should land at the top of the new page; filter tweaks must
  // not move the scroll at all. "No scroll" must be `false`, not `{}`:
  // vue-router treats any truthy return as a scroll command (an empty one
  // scrolls to the current position), and issuing it aborts any smooth
  // scroll already in flight.
  if (to.path === from.path) {
    return to.query.page !== from.query.page ? { top: 0 } : false
  }
  return { top: 0 }
}

export const scrollBehavior: RouterScrollBehavior = (to, from, savedPosition) =>
  resolveScroll(to, from, savedPosition)
