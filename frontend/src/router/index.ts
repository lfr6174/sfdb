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

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
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
