import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useRecords } from '../hooks/useRecords'
import { ResearchRecord } from '../types'
import LoadingSpinner from '../components/LoadingSpinner'

const RecordsPage = () => {
  const [page, setPage] = useState(1)
  const [perPage] = useState(10)

  const { data, isLoading, isError } = useRecords(page, perPage)

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-white">Records</h1>
          <p className="mt-2 text-slate-400">Browse, edit, or delete research records.</p>
        </div>
        <Link
          to="/records/new"
          className="inline-flex items-center rounded-full bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400"
        >
          Create record
        </Link>
      </div>

      <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
        {isLoading ? (
          <LoadingSpinner />
        ) : isError ? (
          <p className="rounded-3xl border border-rose-500/20 bg-rose-500/10 p-6 text-sm text-rose-200">Unable to load records.</p>
        ) : data?.items.length ? (
          <div className="space-y-4">
            <div className="overflow-hidden rounded-3xl border border-slate-800">
              <table className="min-w-full border-separate border-spacing-0 text-left text-sm">
                <thead className="bg-slate-950/90 text-slate-400">
                  <tr>
                    <th className="px-4 py-4">Title</th>
                    <th className="px-4 py-4">Type</th>
                    <th className="px-4 py-4">Status</th>
                    <th className="px-4 py-4">DOI</th>
                    <th className="px-4 py-4">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {data.items.map((record: ResearchRecord) => (
                    <tr key={record.id} className="border-t border-slate-800 bg-slate-950/90 transition hover:bg-slate-900/80">
                      <td className="px-4 py-4 text-slate-100">{record.title}</td>
                      <td className="px-4 py-4 text-slate-300">{record.record_type}</td>
                      <td className="px-4 py-4 text-slate-300">{record.status}</td>
                      <td className="px-4 py-4 text-slate-300">{record.doi}</td>
                      <td className="px-4 py-4 text-slate-300">
                        <Link to={`/records/${record.id}`} className="text-cyan-300 hover:text-cyan-100">
                          View
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
                  className="rounded-full border border-slate-700 bg-slate-900/90 px-4 py-2 text-sm transition hover:border-cyan-500/40 hover:text-cyan-100"
                  disabled={!data.pagination.has_previous}
                  onClick={() => setPage((current) => Math.max(current - 1, 1))}
                >
                  Previous
                </button>
                <button
                  className="rounded-full border border-slate-700 bg-slate-900/90 px-4 py-2 text-sm transition hover:border-cyan-500/40 hover:text-cyan-100"
                  disabled={!data.pagination.has_next}
                  onClick={() => setPage((current) => current + 1)}
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="rounded-3xl border border-slate-800 bg-slate-950/80 p-8 text-slate-300">
            <p className="text-lg font-semibold text-white">No records found.</p>
            <p className="mt-2 text-sm text-slate-400">Create a new record to populate the table.</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default RecordsPage
