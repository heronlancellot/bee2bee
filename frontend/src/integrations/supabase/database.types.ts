export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  graphql_public: {
    Tables: {
      [_ in never]: never
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      graphql: {
        Args: {
          extensions?: Json
          operationName?: string
          query?: string
          variables?: Json
        }
        Returns: Json
      }
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
  public: {
    Tables: {
      chat_messages: {
        Row: {
          content: string
          created_at: string | null
          id: string
          model_name: string | null
          repo_ids: string[] | null
          role: Database["public"]["Enums"]["message_role"]
          sources: Json | null
          tokens_used: number | null
          user_id: string
        }
        Insert: {
          content: string
          created_at?: string | null
          id?: string
          model_name?: string | null
          repo_ids?: string[] | null
          role: Database["public"]["Enums"]["message_role"]
          sources?: Json | null
          tokens_used?: number | null
          user_id: string
        }
        Update: {
          content?: string
          created_at?: string | null
          id?: string
          model_name?: string | null
          repo_ids?: string[] | null
          role?: Database["public"]["Enums"]["message_role"]
          sources?: Json | null
          tokens_used?: number | null
          user_id?: string
        }
        Relationships: []
      }
      code_chunks: {
        Row: {
          chunk_id: string
          chunk_type: Database["public"]["Enums"]["chunk_type"] | null
          code: string
          created_at: string | null
          docstring: string | null
          end_line: number | null
          file_hash: string
          file_path: string
          lines_of_code: number | null
          module: string | null
          name: string | null
          repo_id: string
          signature: string | null
          start_line: number | null
        }
        Insert: {
          chunk_id: string
          chunk_type?: Database["public"]["Enums"]["chunk_type"] | null
          code: string
          created_at?: string | null
          docstring?: string | null
          end_line?: number | null
          file_hash: string
          file_path: string
          lines_of_code?: number | null
          module?: string | null
          name?: string | null
          repo_id: string
          signature?: string | null
          start_line?: number | null
        }
        Update: {
          chunk_id?: string
          chunk_type?: Database["public"]["Enums"]["chunk_type"] | null
          code?: string
          created_at?: string | null
          docstring?: string | null
          end_line?: number | null
          file_hash?: string
          file_path?: string
          lines_of_code?: number | null
          module?: string | null
          name?: string | null
          repo_id?: string
          signature?: string | null
          start_line?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "code_chunks_repo_id_file_path_fkey"
            columns: ["repo_id", "file_path"]
            isOneToOne: false
            referencedRelation: "file_metadata"
            referencedColumns: ["repo_id", "file_path"]
          },
          {
            foreignKeyName: "code_chunks_repo_id_fkey"
            columns: ["repo_id"]
            isOneToOne: false
            referencedRelation: "repositories"
            referencedColumns: ["id"]
          },
        ]
      }
      embeddings: {
        Row: {
          chunk_id: string
          created_at: string | null
          embedding: string
          id: string
          model_name: string | null
        }
        Insert: {
          chunk_id: string
          created_at?: string | null
          embedding: string
          id?: string
          model_name?: string | null
        }
        Update: {
          chunk_id?: string
          created_at?: string | null
          embedding?: string
          id?: string
          model_name?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "embeddings_chunk_id_fkey"
            columns: ["chunk_id"]
            isOneToOne: true
            referencedRelation: "code_chunks"
            referencedColumns: ["chunk_id"]
          },
        ]
      }
      file_metadata: {
        Row: {
          file_hash: string
          file_path: string
          id: string
          indexed_at: string | null
          language: string | null
          last_commit_author: string | null
          last_commit_date: string | null
          last_commit_sha: string | null
          last_modified: string | null
          lines: number | null
          repo_id: string
          size_bytes: number | null
        }
        Insert: {
          file_hash: string
          file_path: string
          id?: string
          indexed_at?: string | null
          language?: string | null
          last_commit_author?: string | null
          last_commit_date?: string | null
          last_commit_sha?: string | null
          last_modified?: string | null
          lines?: number | null
          repo_id: string
          size_bytes?: number | null
        }
        Update: {
          file_hash?: string
          file_path?: string
          id?: string
          indexed_at?: string | null
          language?: string | null
          last_commit_author?: string | null
          last_commit_date?: string | null
          last_commit_sha?: string | null
          last_modified?: string | null
          lines?: number | null
          repo_id?: string
          size_bytes?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "file_metadata_repo_id_fkey"
            columns: ["repo_id"]
            isOneToOne: false
            referencedRelation: "repositories"
            referencedColumns: ["id"]
          },
        ]
      }
      profiles: {
        Row: {
          avatar_url: string | null
          bio: string | null
          created_at: string | null
          full_name: string | null
          github_id: number | null
          github_username: string | null
          id: string
          updated_at: string | null
        }
        Insert: {
          avatar_url?: string | null
          bio?: string | null
          created_at?: string | null
          full_name?: string | null
          github_id?: number | null
          github_username?: string | null
          id: string
          updated_at?: string | null
        }
        Update: {
          avatar_url?: string | null
          bio?: string | null
          created_at?: string | null
          full_name?: string | null
          github_id?: number | null
          github_username?: string | null
          id?: string
          updated_at?: string | null
        }
        Relationships: []
      }
      repositories: {
        Row: {
          created_at: string | null
          default_branch: string | null
          description: string | null
          expires_at: string | null
          forks: number | null
          full_name: string
          github_id: number | null
          id: string
          indexed_at: string | null
          indexing_error: string | null
          indexing_started_at: string | null
          language: string | null
          last_interaction_at: string | null
          license: string | null
          open_issues: number | null
          size_bytes: number | null
          stars: number | null
          status: Database["public"]["Enums"]["repo_status"] | null
          topics: string[] | null
          total_chunks: number | null
          total_embeddings: number | null
          total_files: number | null
          updated_at: string | null
        }
        Insert: {
          created_at?: string | null
          default_branch?: string | null
          description?: string | null
          expires_at?: string | null
          forks?: number | null
          full_name: string
          github_id?: number | null
          id?: string
          indexed_at?: string | null
          indexing_error?: string | null
          indexing_started_at?: string | null
          language?: string | null
          last_interaction_at?: string | null
          license?: string | null
          open_issues?: number | null
          size_bytes?: number | null
          stars?: number | null
          status?: Database["public"]["Enums"]["repo_status"] | null
          topics?: string[] | null
          total_chunks?: number | null
          total_embeddings?: number | null
          total_files?: number | null
          updated_at?: string | null
        }
        Update: {
          created_at?: string | null
          default_branch?: string | null
          description?: string | null
          expires_at?: string | null
          forks?: number | null
          full_name?: string
          github_id?: number | null
          id?: string
          indexed_at?: string | null
          indexing_error?: string | null
          indexing_started_at?: string | null
          language?: string | null
          last_interaction_at?: string | null
          license?: string | null
          open_issues?: number | null
          size_bytes?: number | null
          stars?: number | null
          status?: Database["public"]["Enums"]["repo_status"] | null
          topics?: string[] | null
          total_chunks?: number | null
          total_embeddings?: number | null
          total_files?: number | null
          updated_at?: string | null
        }
        Relationships: []
      }
      user_repositories: {
        Row: {
          added_at: string | null
          id: string
          is_selected: boolean | null
          repo_id: string
          user_id: string
        }
        Insert: {
          added_at?: string | null
          id?: string
          is_selected?: boolean | null
          repo_id: string
          user_id: string
        }
        Update: {
          added_at?: string | null
          id?: string
          is_selected?: boolean | null
          repo_id?: string
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "user_repositories_repo_id_fkey"
            columns: ["repo_id"]
            isOneToOne: false
            referencedRelation: "repositories"
            referencedColumns: ["id"]
          },
        ]
      }
    }
    Views: {
      user_selected_repos_view: {
        Row: {
          added_at: string | null
          description: string | null
          expires_at: string | null
          full_name: string | null
          is_selected: boolean | null
          language: string | null
          last_interaction_at: string | null
          repo_id: string | null
          stars: number | null
          status: Database["public"]["Enums"]["repo_status"] | null
          total_chunks: number | null
          total_files: number | null
          user_id: string | null
        }
        Relationships: [
          {
            foreignKeyName: "user_repositories_repo_id_fkey"
            columns: ["repo_id"]
            isOneToOne: false
            referencedRelation: "repositories"
            referencedColumns: ["id"]
          },
        ]
      }
    }
    Functions: {
      cleanup_expired_repos: {
        Args: { days_expired?: number }
        Returns: {
          deleted_chunks: number
          deleted_embeddings: number
          deleted_repos: number
        }[]
      }
      connect_github_account: {
        Args: {
          avatar_url_param: string
          github_id_param: number
          github_username_param: string
          user_id: string
        }
        Returns: undefined
      }
      get_user_selected_repos: {
        Args: { user_uuid: string }
        Returns: string[]
      }
      mark_expired_repos: {
        Args: Record<PropertyKey, never>
        Returns: {
          expired_count: number
        }[]
      }
      search_similar_chunks: {
        Args: {
          match_count?: number
          match_threshold?: number
          query_embedding: string
          user_uuid: string
        }
        Returns: {
          chunk_id: string
          chunk_type: Database["public"]["Enums"]["chunk_type"]
          code: string
          docstring: string
          file_path: string
          name: string
          repo_full_name: string
          repo_id: string
          signature: string
          similarity: number
        }[]
      }
      update_repo_interaction: {
        Args: { repo_uuid: string }
        Returns: undefined
      }
    }
    Enums: {
      chunk_type: "file" | "function" | "class" | "interface" | "module"
      message_role: "user" | "assistant" | "system"
      repo_status: "pending" | "indexing" | "ready" | "expired" | "failed"
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

export type Tables<
  PublicTableNameOrOptions extends
    | keyof (Database["public"]["Tables"] & Database["public"]["Views"])
    | { schema: keyof Database },
  TableName extends PublicTableNameOrOptions extends { schema: keyof Database }
    ? keyof (Database[PublicTableNameOrOptions["schema"]]["Tables"] &
        Database[PublicTableNameOrOptions["schema"]]["Views"])
    : never = never
> = PublicTableNameOrOptions extends { schema: keyof Database }
  ? (Database[PublicTableNameOrOptions["schema"]]["Tables"] &
      Database[PublicTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : PublicTableNameOrOptions extends keyof (Database["public"]["Tables"] &
      Database["public"]["Views"])
  ? (Database["public"]["Tables"] &
      Database["public"]["Views"])[PublicTableNameOrOptions] extends {
      Row: infer R
    }
    ? R
    : never
  : never

export type TablesInsert<
  PublicTableNameOrOptions extends
    | keyof Database["public"]["Tables"]
    | { schema: keyof Database },
  TableName extends PublicTableNameOrOptions extends { schema: keyof Database }
    ? keyof Database[PublicTableNameOrOptions["schema"]]["Tables"]
    : never = never
> = PublicTableNameOrOptions extends { schema: keyof Database }
  ? Database[PublicTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : PublicTableNameOrOptions extends keyof Database["public"]["Tables"]
  ? Database["public"]["Tables"][PublicTableNameOrOptions] extends {
      Insert: infer I
    }
    ? I
    : never
  : never

export type TablesUpdate<
  PublicTableNameOrOptions extends
    | keyof Database["public"]["Tables"]
    | { schema: keyof Database },
  TableName extends PublicTableNameOrOptions extends { schema: keyof Database }
    ? keyof Database[PublicTableNameOrOptions["schema"]]["Tables"]
    : never = never
> = PublicTableNameOrOptions extends { schema: keyof Database }
  ? Database[PublicTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : PublicTableNameOrOptions extends keyof Database["public"]["Tables"]
  ? Database["public"]["Tables"][PublicTableNameOrOptions] extends {
      Update: infer U
    }
    ? U
    : never
  : never

export type Enums<
  PublicEnumNameOrOptions extends
    | keyof Database["public"]["Enums"]
    | { schema: keyof Database },
  EnumName extends PublicEnumNameOrOptions extends { schema: keyof Database }
    ? keyof Database[PublicEnumNameOrOptions["schema"]]["Enums"]
    : never = never
> = PublicEnumNameOrOptions extends { schema: keyof Database }
  ? Database[PublicEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : PublicEnumNameOrOptions extends keyof Database["public"]["Enums"]
  ? Database["public"]["Enums"][PublicEnumNameOrOptions]
  : never

// Type aliases for easier use
export type Repository = Tables<"repositories">
export type UserRepository = Tables<"user_repositories">
export type CodeChunk = Tables<"code_chunks">
export type ChatMessage = Tables<"chat_messages">
export type FileMetadata = Tables<"file_metadata">
export type Embedding = Tables<"embeddings">
export type Profile = Tables<"profiles">

// Enum aliases
export type RepoStatus = Enums<"repo_status">
export type ChunkType = Enums<"chunk_type">
export type MessageRole = Enums<"message_role">