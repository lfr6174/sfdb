export interface AgentAlias {
  id: number
  name: string
}

export interface AgentLink {
  id: number
  label: string
  url: string
}

export interface ParticipatedWork {
  id: number
  title: string
  year: number | null
  genre: string
  work_length: string
  roles: string[]
  concepts: { name: string; slug: string }[]
  awards: {
    catalogue_id: number
    title: string
    year: number | null
    category: string
    status: string
  }[]
}

export interface ParticipatedPublication {
  id: number
  title: string
  year: number | null
  source: string
  media: string
  publisher: string
  isbn: string
  note: string
  roles: string[]
}

export interface PersonConcept {
  id: number
  name: string
  slug: string
  works_count: number
}

export interface Person {
  id: number
  name: string
  agent_type: 'person' | 'organization'

  // Detail/Optional fields
  about?: string
  aliases?: AgentAlias[]
  links?: AgentLink[]
  participated_works?: ParticipatedWork[]
  participated_publications?: ParticipatedPublication[]
  concepts?: PersonConcept[]
  updated_at?: string
}
