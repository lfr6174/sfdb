import api from './axios'
import type { PaginatedResponse, Concept } from '../types'

export function fetchConcepts(params?: Record<string, any>) {
  return api.get<PaginatedResponse<Concept>>('/concepts/', { params })
}

export function fetchAllConcepts() {
  return api.get<Concept[]>('/concepts/all/')
}

export function fetchConceptDetail(slug: string) {
  return api.get<Concept>(`/concepts/${slug}/`)
}

export function fetchRandomConcept() {
  return api.get<Concept>('/concepts/random/')
}
