import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ConceptsView from '../views/ConceptsView.vue'
import PersonsView from '../views/PersonsView.vue'
import PersonDetailView from '../views/PersonDetailView.vue'
import ConceptDetailView from '../views/ConceptDetailView.vue'
import WorksView from '../views/WorksView.vue'
import WorkDetailView from '../views/WorkDetailView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/concepts',
      name: 'concepts',
      component: ConceptsView
    },
    {
      path: '/concepts/:slug',
      name: 'concept-detail',
      component: ConceptDetailView,
      props: true
    },
    {
      path: '/persons',
      name: 'persons',
      component: PersonsView
    },
    {
      path: '/persons/:id',
      name: 'person-detail',
      component: PersonDetailView,
      props: true
    },
    {
      path: '/works',
      name: 'works',
      component: WorksView
    },
    {
      path: '/works/:id',
      name: 'work-detail',
      component: WorkDetailView,
      props: true
    }
  ]
})

export default router
