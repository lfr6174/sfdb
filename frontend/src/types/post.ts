export interface Post {
  id: number
  title: string
  created_at: string

  // Detail fields
  body?: string
  is_pinned?: boolean
  author_name?: string
  updated_at?: string
}
