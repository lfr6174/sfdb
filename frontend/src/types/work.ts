import type { AgentMinimal, BylineEntry, CreditGroup } from './common'
import type { Concept } from './concept'

export interface Cycle {
  id: number
  title: string
  note: string
  created_at: string
  updated_at: string
}

export interface WorkConcept {
  id: number
  concept: Concept
  description?: string
}

export interface CatalogueBrief {
  id: number
  title: string
  catalogue_type_display: string
  year: number | null
  curators: AgentMinimal[]
}

export interface WorkCatalogue {
  id: number
  catalogue: CatalogueBrief
  category: string
  status: string
  status_display: string
  note: string
}

export interface WorkAgent {
  id: number
  agent: AgentMinimal
  role: string
  role_display: string
  order: number
}

export interface Publication {
  id: number
  title: string
  source_display: string
  media_display: string
  language_display: string
  year: number | null
  isbn: string
  note: string
  publisher: AgentMinimal | null
  contributions: {
    id: number
    agent: AgentMinimal
    display_name: string
    role: string
    role_display: string
    order: number
  }[]
  manifestation_id?: number
  manifestation_name?: string
  manifestation_display_name?: string
  credit?: CreditGroup[]
}

export interface Work {
  id: number
  title: string
  year: number | null
  byline: BylineEntry[]
  genre_display: string
  work_length_display: string
  work_concepts: WorkConcept[]

  // Detail fields (optional for list views)
  language?: string
  language_display?: string
  genre?: string
  work_length?: string
  description?: string
  cycle?: Cycle | null
  cycle_order?: string | null
  contributions?: WorkAgent[]
  publications?: Publication[]
  work_catalogues?: WorkCatalogue[]
  credit?: CreditGroup[]
  updated_at?: string
}
