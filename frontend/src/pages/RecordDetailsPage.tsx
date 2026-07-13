import { useState } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { fetchRecordById, deleteRecord } from '../services/records'
import { ResearchRecord } from '../types'
import LoadingSpinner from '../components/LoadingSpinner'
import Toast from '../components/Toast'

const RecordDetailsPage = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [toast, setToast] = useState<string | null>(null)

  const { data, isLoading, isError } = useQuery<ResearchRecord>({
    queryKey: ['record', id],
    queryFn: () => fetchRecordById(id!),
    enabled: Boolean(id),
  })

  const deleteMutation = useMutation({
    mutationFn: () => deleteRecord(id!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['records'] })
      setToast('Record deleted successfully')
      setTimeout(() => navigate('/records'), 500)
    },
    onError: () => {
      setToast('Failed to delete record')
    },
  })

  return (
    <div className="space-y-8">
      {toast ? <Toast title="Notification" message={toast} variant="success" /> : null}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-white">Record Details</h1>
          <p className="mt-2 text-slate-400">Review record contents or make edits.</p>
        </div>
        <div className="flex flex-wrap gap-3">
          <Link
            to={`/records/${id}/edit`}
            className="inline-flex items-center rounded-full bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400"
          >
            Edit
          </Link>
          <button
            onClick={() => deleteMutation.mutate()}
            className="inline-flex items-center rounded-full border border-rose-500 px-4 py-2 text-sm font-semibold text-rose-200 transition hover:bg-rose-500/10"
          >
            Delete
          </button>
        </div>
      </div>

      <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
        {isLoading ? (
          <LoadingSpinner />
        ) : isError ? (
          <p className="rounded-3xl border border-rose-500/20 bg-rose-500/10 p-6 text-sm text-rose-200">Unable to load record details.</p>
        ) : data ? (
          <div className="space-y-6">
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <p className="text-sm uppercase tracking-[0.24em] text-cyan-400">Title</p>
                <p className="mt-2 text-xl font-semibold text-white">{data.title}</p>
              </div>
              <div>
                <p className="text-sm uppercase tracking-[0.24em] text-cyan-400">Status</p>
                <p className="mt-2 text-xl font-semibold text-white">{data.status}</p>
              </div>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <p className="text-sm uppercase tracking-[0.24em] text-cyan-400">Type</p>
                <p className="mt-2 text-white">{data.record_type}</p>
              </div>
              <div>
                <p className="text-sm uppercase tracking-[0.24em] text-cyan-400">DOI</p>
                <p className="mt-2 text-white">{data.doi}</p>
              </div>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <p className="text-sm uppercase tracking-[0.24em] text-cyan-400">License</p>
                <p className="mt-2 text-white">{data.license}</p>
              </div>
              <div>
                <p className="text-sm uppercase tracking-[0.24em] text-cyan-400">Publication</p>
                <p className="mt-2 text-white">{data.publication_date ?? 'N/A'}</p>
              </div>
            </div>
            <div>
              <p className="text-sm uppercase tracking-[0.24em] text-cyan-400">Description</p>
              <p className="mt-2 rounded-3xl border border-slate-800 bg-slate-950/80 p-4 text-slate-300">{data.description}</p>
            </div>
          </div>
        ) : (
          <p className="text-slate-300">Record not found.</p>
        )}
      </div>
    </div>
  )
}

export default RecordDetailsPage
