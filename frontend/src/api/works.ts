import api from './axios'
import type { PaginatedResponse, Work } from '../types'

export function fetchWorks(params: Record<string, string | number | boolean>) {
  return api.get<PaginatedResponse<Work>>('/works/', { params })
}

export function fetchWorkDetail(id: string | number) {
  return api.get<Work>(`/works/${id}/`)
}
