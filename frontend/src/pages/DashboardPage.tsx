import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { fetchRecords } from '../services/records'
import { RecordsResponse } from '../types'
import LoadingSpinner from '../components/LoadingSpinner'

const DashboardPage = () => {
  const { data, isLoading, isError } = useQuery<RecordsResponse>({
    queryKey: ['dashboard-records'],
    queryFn: () => fetchRecords(1, 5),
  })

  return (
    <div className="space-y-8">
      <section className="grid gap-4 sm:grid-cols-3">
        <article className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
          <p className="text-sm text-slate-400">Active records</p>
          <p className="mt-4 text-4xl font-semibold text-white">{data?.pagination.total_items ?? '—'}</p>
          <p className="mt-2 text-sm text-slate-500">Total records indexed by the backend.</p>
        </article>

        <article className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
          <p className="text-sm text-slate-400">Latest status</p>
          <p className="mt-4 text-4xl font-semibold text-white">{data?.items[0]?.status ?? '—'}</p>
          <p className="mt-2 text-sm text-slate-500">Status of the most recently created record.</p>
        </article>

        <article className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
          <p className="text-sm text-slate-400">Open Search</p>
          <p className="mt-4 text-4xl font-semibold text-white">Enabled</p>
          <p className="mt-2 text-sm text-slate-500">Search page connects to /api/search/records.</p>
        </article>
      </section>

      <section className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-white">Dashboard</h1>
            <p className="mt-2 text-slate-400">Manage records and perform OpenSearch queries from the UI.</p>
          </div>
          <Link
            to="/records/new"
            className="inline-flex items-center justify-center rounded-full bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400"
          >
            Create record
          </Link>
        </div>

        <div className="mt-8">
          {isLoading ? (
            <LoadingSpinner />
          ) : isError ? (
            <p className="rounded-3xl border border-rose-500/20 bg-rose-500/10 p-6 text-sm text-rose-200">Unable to load dashboard summary.</p>
          ) : data?.items.length ? (
            <div className="grid gap-4 md:grid-cols-2">
              {data.items.map((record) => (
                <div key={record.id} className="rounded-3xl border border-slate-800 bg-slate-950/80 p-5">
                  <p className="text-sm uppercase tracking-[0.24em] text-cyan-400">{record.record_type}</p>
                  <h2 className="mt-3 text-xl font-semibold text-white">{record.title}</h2>
                  <p className="mt-3 text-sm leading-6 text-slate-300">{record.description}</p>
                </div>
              ))}
            </div>
          ) : (
            <div className="rounded-3xl border border-slate-800 bg-slate-950/80 p-8 text-slate-300">
              <p className="text-lg font-semibold text-white">No records available yet.</p>
              <p className="mt-2 text-sm text-slate-400">Start by creating a record using the button above.</p>
            </div>
          )}
        </div>
      </section>
    </div>
  )
}

export default DashboardPage
