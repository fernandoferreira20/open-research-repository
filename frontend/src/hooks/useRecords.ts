import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { fetchRecordById, fetchRecords } from '../services/records'
import { RecordsResponse, ResearchRecord } from '../types'

export const useRecords = (page: number, per_page: number, filter?: Record<string, string>) => {
  return useQuery<RecordsResponse>({
    queryKey: ['records', { page, per_page, filter }],
    queryFn: () => fetchRecords(page, per_page, filter),
    placeholderData: keepPreviousData,
  })
}

export const useRecord = (id: string) => {
  return useQuery<ResearchRecord>({
    queryKey: ['record', id],
    queryFn: () => fetchRecordById(id),
  })
}
