import api from './axios'
import type { PaginatedResponse, Post } from '../types'

export function fetchPosts(params?: Record<string, string | number | boolean>) {
  return api.get<PaginatedResponse<Post>>('/posts/', { params })
}

export function fetchPostDetail(id: string | number) {
  return api.get<Post>(`/posts/${id}/`)
}

export function fetchActivePinnedPost() {
  return api.get<Post>('/posts/active-pinned/')
}
