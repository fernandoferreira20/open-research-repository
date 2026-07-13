import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { useSearchRecords } from '../hooks/useSearch'
import LoadingSpinner from '../components/LoadingSpinner'
import { Search, ArrowRight, ChevronLeft, ChevronRight } from 'lucide-react'
import { SearchRecord } from '../types'

const statusOptions = ['draft', 'published', 'archived'] as const
const typeOptions = ['paper', 'dataset', 'software', 'presentation', 'other'] as const
const sortOptions = [
  { value: 'relevance', label: 'Relevance' },
  { value: 'created_at', label: 'Created At' },
  { value: 'updated_at', label: 'Updated At' },
  { value: 'publication_date', label: 'Publication Date' },
  { value: 'title', label: 'Title' },
] as const

const SearchPage = () => {
  const [q, setQ] = useState('')
  const [status, setStatus] = useState<string>('')
  const [recordType, setRecordType] = useState<string>('')
  const [sort, setSort] = useState('relevance')
  const [order, setOrder] = useState<'asc' | 'desc'>('desc')
  const [page, setPage] = useState(1)
  const [perPage, setPerPage] = useState(10)

  const searchParams = useMemo(
    () => ({
      q: q || undefined,
      status: status || undefined,
      record_type: recordType || undefined,
      sort,
      order,
      page,
      per_page: perPage,
    }),
    [q, status, recordType, sort, order, page, perPage],
  )

  const { data, isLoading, isError } = useSearchRecords(searchParams)

  const handleSearch = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setPage(1)
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-white">Search</h1>
          <p className="mt-2 text-slate-400">Query the OpenSearch index and view relevance scores.</p>
        </div>
      </div>

      <section className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
        <form onSubmit={handleSearch} className="grid gap-4 lg:grid-cols-[1.6fr_0.8fr]">
          <label className="space-y-2 text-sm text-slate-300">
            <span>Search query</span>
            <div className="relative">
              <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
              <input
                value={q}
                onChange={(event) => setQ(event.target.value)}
                placeholder="Search title, description, DOI"
                className="w-full rounded-3xl border border-slate-700 bg-slate-950/90 px-12 py-3 text-slate-100 outline-none transition focus:border-cyan-400"
              />
            </div>
          </label>

          <button className="h-full rounded-3xl bg-cyan-500 px-6 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400">
            Search
          </button>

          <div className="grid gap-4 sm:grid-cols-2 lg:col-span-2">
            <label className="space-y-2 text-sm text-slate-300">
              <span>Status</span>
              <select
                value={status}
                onChange={(event) => setStatus(event.target.value)}
                className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none transition focus:border-cyan-400"
              >
                <option value="">All statuses</option>
                {statusOptions.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </label>

            <label className="space-y-2 text-sm text-slate-300">
              <span>Record type</span>
              <select
                value={recordType}
                onChange={(event) => setRecordType(event.target.value)}
                className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none transition focus:border-cyan-400"
              >
                <option value="">All types</option>
                {typeOptions.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </label>

            <label className="space-y-2 text-sm text-slate-300">
              <span>Sort</span>
              <select
                value={sort}
                onChange={(event) => setSort(event.target.value)}
                className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none transition focus:border-cyan-400"
              >
                {sortOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>

            <label className="space-y-2 text-sm text-slate-300">
              <span>Order</span>
              <select
                value={order}
                onChange={(event) => setOrder(event.target.value as 'asc' | 'desc')}
                className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none transition focus:border-cyan-400"
              >
                <option value="desc">Descending</option>
                <option value="asc">Ascending</option>
              </select>
            </label>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:col-span-2">
            <label className="space-y-2 text-sm text-slate-300">
              <span>Page</span>
              <input
                type="number"
                min={1}
                value={page}
                onChange={(event) => setPage(Number(event.target.value) || 1)}
                className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none transition focus:border-cyan-400"
              />
            </label>
            <label className="space-y-2 text-sm text-slate-300">
              <span>Per page</span>
              <input
                type="number"
                min={1}
                max={100}
                value={perPage}
                onChange={(event) => setPerPage(Number(event.target.value) || 10)}
                className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none transition focus:border-cyan-400"
              />
            </label>
          </div>
        </form>
      </section>

      <section className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
        {isLoading ? (
          <LoadingSpinner />
        ) : isError ? (
          <p className="rounded-3xl border border-rose-500/20 bg-rose-500/10 p-6 text-sm text-rose-200">Search failed. Please try again.</p>
        ) : data?.items.length ? (
          <div className="space-y-6">
            <div className="overflow-hidden rounded-3xl border border-slate-800">
              <table className="min-w-full border-separate border-spacing-0 text-left text-sm">
                <thead className="bg-slate-950/90 text-slate-400">
                  <tr>
                    <th className="px-4 py-4">Title</th>
                    <th className="px-4 py-4">Score</th>
                    <th className="px-4 py-4">Type</th>
                    <th className="px-4 py-4">Status</th>
                    <th className="px-4 py-4">DOI</th>
                    <th className="px-4 py-4">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {data.items.map((result: SearchRecord) => (
                    <tr key={result.id} className="border-t border-slate-800 bg-slate-950/90 transition hover:bg-slate-900/80">
                      <td className="px-4 py-4 text-slate-100">{result.title}</td>
                      <td className="px-4 py-4 text-slate-300">{result.score?.toFixed(2) ?? 'N/A'}</td>
                      <td className="px-4 py-4 text-slate-300">{result.record_type}</td>
                      <td className="px-4 py-4 text-slate-300">{result.status}</td>
                      <td className="px-4 py-4 text-slate-300">{result.doi}</td>
                      <td className="px-4 py-4 text-slate-300">
                        <Link to={`/records/${result.id}`} className="inline-flex items-center gap-2 text-cyan-300 hover:text-cyan-100">
                          <ArrowRight className="h-4 w-4" />
                          Details
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="flex flex-wrap items-center justify-between gap-3 text-sm text-slate-300">
              <p>
                Page {data.pagination.page} of {data.pagination.total_pages}
              </p>
              <div className="flex items-center gap-3">
                <button
                  className="inline-flex items-center gap-2 rounded-full border border-slate-700 bg-slate-900/90 px-4 py-2 transition hover:border-cyan-500/40 hover:text-cyan-100 disabled:cursor-not-allowed disabled:opacity-60"
                  onClick={() => setPage(Math.max(page - 1, 1))}
                  disabled={!data.pagination.has_previous}
                >
                  <ChevronLeft className="h-4 w-4" /> Previous
                </button>
                <button
                  className="inline-flex items-center gap-2 rounded-full border border-slate-700 bg-slate-900/90 px-4 py-2 transition hover:border-cyan-500/40 hover:text-cyan-100 disabled:cursor-not-allowed disabled:opacity-60"
                  onClick={() => setPage(page + 1)}
                  disabled={!data.pagination.has_next}
                >
                  Next <ChevronRight className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="rounded-3xl border border-slate-800 bg-slate-950/80 p-8 text-slate-300">
            <p className="text-lg font-semibold text-white">No search results yet.</p>
            <p className="mt-2 text-sm text-slate-400">Enter a query and submit to see matching records.</p>
          </div>
        )}
      </section>
    </div>
  )
}

export default SearchPage
