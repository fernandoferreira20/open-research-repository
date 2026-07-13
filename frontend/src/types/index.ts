export type RecordStatus = 'draft' | 'published' | 'archived'
export type RecordType = 'paper' | 'dataset' | 'software' | 'presentation' | 'other'

export interface ResearchRecord {
  id: string
  title: string
  description: string
  record_type: RecordType
  status: RecordStatus
  license: string
  doi: string
  publication_date: string | null
  created_at: string | null
  updated_at: string | null
}

export interface SearchRecord extends ResearchRecord {
  score: number | null
}

export interface Pagination {
  page: number
  per_page: number
  total_items: number
  total_pages: number
  has_next: boolean
  has_previous: boolean
}

export interface RecordsResponse {
  items: ResearchRecord[]
  pagination: Pagination
}

export interface SearchResponse {
  items: SearchRecord[]
  pagination: Pagination
}
