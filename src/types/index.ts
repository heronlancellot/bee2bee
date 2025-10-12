export interface Repository {
  id: string
  name: string
  full_name: string
  owner: string
  description: string | null
  is_private: boolean
  is_favorite: boolean
  language: string | null
  stars: number
  indexed_at: string | null
  complexity_score: number | null
  agent_id: string | null
  branches?: string[]
  default_branch?: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
  sources?: CodeSource[]
}

export interface CodeSource {
  file_path: string
  line_start: number
  line_end: number
  repository: string
  content: string
}

export interface ChatSession {
  id: string
  title: string
  created_at: string
  updated_at: string
  repository_ids: string[]
  messages: ChatMessage[]
}
