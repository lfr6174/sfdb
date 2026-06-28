import api from './axios'
import type { Page } from '../types'

export function fetchPageDetail(slug: string) {
  return api.get<Page>(`/pages/${slug}/`)
}
