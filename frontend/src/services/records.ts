import { api } from './api'
import { RecordsResponse, ResearchRecord, SearchResponse } from '../types'

export type RecordInput = Omit<ResearchRecord, 'id' | 'created_at' | 'updated_at'>

export const fetchRecords = async (
  page = 1,
  per_page = 10,
  filter?: Record<string, string>,
): Promise<RecordsResponse> => {
  const response = await api.get<RecordsResponse>('/records', {
    params: { page, per_page, ...filter },
  })
  return response.data
}

export const fetchRecordById = async (id: string): Promise<ResearchRecord> => {
  const response = await api.get<ResearchRecord>(`/records/${id}`)
  return response.data
}

export const createRecord = async (payload: RecordInput): Promise<ResearchRecord> => {
  const response = await api.post<ResearchRecord>('/records', payload)
  return response.data
}

export const updateRecord = async (id: string, payload: RecordInput): Promise<ResearchRecord> => {
  const response = await api.put<ResearchRecord>(`/records/${id}`, payload)
  return response.data
}

export const deleteRecord = async (id: string): Promise<void> => {
  await api.delete(`/records/${id}`)
}

export const searchRecords = async (
  params: Record<string, string | number | undefined>,
): Promise<SearchResponse> => {
  const response = await api.get<SearchResponse>('/search/records', { params })
  return response.data
}
