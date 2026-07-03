import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

// Lazy-loaded routes
const ConceptsView = () => import('../views/ConceptsView.vue')
const PersonsView = () => import('../views/PersonsView.vue')
const PersonDetailView = () => import('../views/PersonDetailView.vue')
const ConceptDetailView = () => import('../views/ConceptDetailView.vue')
const WorksView = () => import('../views/WorksView.vue')
const WorkDetailView = () => import('../views/WorkDetailView.vue')
const PostsView = () => import('../views/PostsView.vue')
const PostDetailView = () => import('../views/PostDetailView.vue')
const PageDetailView = () => import('../views/PageDetailView.vue')
const NotFoundView = () => import('../views/NotFoundView.vue')

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

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return waitToRestore(savedPosition)
    }
    // Same path = a query-only navigation (filters syncing to the URL),
    // not a page change — leave the scroll position alone.
    if (to.path === from.path) {
      return {}
    }
    return { top: 0 }
  },
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/concepts',
      name: 'concepts',
      component: ConceptsView,
    },
    {
      path: '/concepts/:slug',
      name: 'concept-detail',
      component: ConceptDetailView,
      props: true,
    },
    {
      path: '/persons',
      name: 'persons',
      component: PersonsView,
    },
    {
      path: '/persons/:id',
      name: 'person-detail',
      component: PersonDetailView,
      props: true,
    },
    {
      path: '/works',
      name: 'works',
      component: WorksView,
    },
    {
      path: '/works/:id',
      name: 'work-detail',
      component: WorkDetailView,
      props: true,
    },
    {
      path: '/posts',
      name: 'posts',
      component: PostsView,
    },
    {
      path: '/posts/:id',
      name: 'post-detail',
      component: PostDetailView,
      props: true,
    },
    {
      path: '/pages/:slug',
      name: 'page-detail',
      component: PageDetailView,
      props: true,
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: NotFoundView,
    },
  ],
})

export default router
