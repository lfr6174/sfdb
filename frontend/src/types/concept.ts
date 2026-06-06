import type { BylineEntry } from './common'

export interface ConceptLink {
  id: number
  title: string
  url: string
  order: number
}

export interface ConceptWorkEntry {
  id: number
  work: number
  work_title: string
  year: number | null
  description: string
}

export interface Concept {
  id: number
  name: string
  slug: string
  category: 'novum' | 'narrative' | 'theme'

  // Optional/Detail fields
  is_featured?: boolean
  featured_order?: number
  description?: string
  works_count?: number
  related_concepts?: Concept[]
  work_concepts?: ConceptWorkEntry[]
  links?: ConceptLink[]
  created_at?: string
  updated_at?: string

  // Custom endpoint specific
  random_works?: {
    id: number
    title: string
    year: number | null
    genre_display: string
    work_length_display: string
    byline: BylineEntry[]
  }[]
}
