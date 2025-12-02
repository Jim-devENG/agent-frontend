import { useState, useEffect, useCallback } from 'react'

export interface PaginatedResponse<T> {
  data: T[]
  page: number
  limit: number
  total: number
  totalPages: number
}

export interface UsePaginatedFetchOptions {
  fetchFn: (page: number, limit: number) => Promise<PaginatedResponse<any>>
  initialPage?: number
  limit?: number
  autoLoad?: boolean
}

export interface UsePaginatedFetchReturn<T> {
  page: number
  setPage: (page: number) => void
  data: T[]
  totalPages: number
  total: number
  loading: boolean
  error: string | null
  limit: number
  refresh: () => Promise<void>
  goToNext: () => void
  goToPrev: () => void
  canGoNext: boolean
  canGoPrev: boolean
}

export function usePaginatedFetch<T = any>(
  options: UsePaginatedFetchOptions
): UsePaginatedFetchReturn<T> {
  const {
    fetchFn,
    initialPage = 1,
    limit = 10,
    autoLoad = true,
  } = options

  const [page, setPage] = useState(initialPage)
  const [data, setData] = useState<T[]>([])
  const [totalPages, setTotalPages] = useState(0)
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetchFn(page, limit)
      
      // Handle both standardized format and backward compatibility
      const items = response.data || (response as any).prospects || (response as any).items || []
      const totalPages = response.totalPages || (response as any).total_pages || 0
      const total = response.total || 0
      
      setData(items)
      setTotalPages(totalPages)
      setTotal(total)
    } catch (err: any) {
      setError(err.message || 'Failed to load data')
      setData([])
      setTotalPages(0)
      setTotal(0)
    } finally {
      setLoading(false)
    }
  }, [fetchFn, page, limit])

  useEffect(() => {
    if (autoLoad) {
      loadData()
    }
  }, [loadData, autoLoad])

  const goToNext = useCallback(() => {
    setPage((prev) => Math.min(prev + 1, totalPages))
  }, [totalPages])

  const goToPrev = useCallback(() => {
    setPage((prev) => Math.max(prev - 1, 1))
  }, [])

  const canGoNext = page < totalPages
  const canGoPrev = page > 1

  return {
    page,
    setPage,
    data,
    totalPages,
    total,
    loading,
    error,
    limit,
    refresh: loadData,
    goToNext,
    goToPrev,
    canGoNext,
    canGoPrev,
  }
}

