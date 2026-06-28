export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface AgentMinimal {
  id: number
  name: string
  agent_type: 'person' | 'organization'
}

export interface BylineEntry {
  id: number
  text: string
  agent_type: string
}

export interface CreditGroup {
  role: string
  agents: BylineEntry[]
}
