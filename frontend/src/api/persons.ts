import api from './axios'
import type { PaginatedResponse, Person } from '../types'

export function fetchPersons(params?: Record<string, any>) {
  return api.get<PaginatedResponse<Person>>('/persons/', { params })
}

export function fetchPersonDetail(id: string | number) {
  return api.get<Person>(`/persons/${id}/`)
}
