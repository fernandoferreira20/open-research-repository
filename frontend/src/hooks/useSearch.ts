import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { searchRecords } from '../services/records'
import { SearchResponse } from '../types'

export const useSearchRecords = (params: Record<string, string | number | undefined>) => {
  return useQuery<SearchResponse>({
    queryKey: ['search', params],
    queryFn: () => searchRecords(params),
    placeholderData: keepPreviousData,
  })
}
