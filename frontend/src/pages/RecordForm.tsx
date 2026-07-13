import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { RecordInput, createRecord, updateRecord, fetchRecordById } from '../services/records'
import { useNavigate, useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ResearchRecord } from '../types'
import LoadingSpinner from '../components/LoadingSpinner'
import Toast from '../components/Toast'

type RecordFormProps = {
  mode: 'create' | 'edit'
}

const statusOptions = ['draft', 'published', 'archived'] as const
const typeOptions = ['paper', 'dataset', 'software', 'presentation', 'other'] as const

const RecordForm = ({ mode }: RecordFormProps) => {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { id } = useParams<{ id: string }>()
  const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm<RecordInput>()
  const [toast, setToast] = useState<string | null>(null)

  const { data, isLoading: isLoadingRecord } = useQuery<ResearchRecord>({
    queryKey: ['record', id],
    queryFn: () => fetchRecordById(id!),
    enabled: mode === 'edit' && Boolean(id),
  })

  useEffect(() => {
    if (data) {
      reset({
        title: data.title,
        description: data.description,
        record_type: data.record_type,
        status: data.status,
        license: data.license,
        doi: data.doi,
        publication_date: data.publication_date ?? '',
      })
    }
  }, [data, reset])

  const createMutation = useMutation({
    mutationFn: (payload: RecordInput) => createRecord(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['records'] })
      setToast('Record created successfully')
      setTimeout(() => navigate('/records'), 600)
    },
    onError: () => {
      setToast('Failed to create record')
    },
  })

  const updateMutation = useMutation({
    mutationFn: (payload: RecordInput) => updateRecord(id!, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['records'] })
      queryClient.invalidateQueries({ queryKey: ['record', id] })
      setToast('Record updated successfully')
      setTimeout(() => navigate(`/records/${id}`), 600)
    },
    onError: () => {
      setToast('Failed to update record')
    },
  })

  const onSubmit = (values: RecordInput) => {
    if (mode === 'create') {
      createMutation.mutate(values)
    } else {
      updateMutation.mutate(values)
    }
  }

  if (mode === 'edit' && isLoadingRecord) {
    return <LoadingSpinner />
  }

  return (
    <div className="space-y-8">
      {toast ? <Toast title="Notification" message={toast} variant="success" /> : null}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-white">{mode === 'create' ? 'Create Record' : 'Edit Record'}</h1>
          <p className="mt-2 text-slate-400">{mode === 'create' ? 'Add a new research record.' : 'Update the existing record details.'}</p>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 space-y-6">
        <div className="grid gap-6 lg:grid-cols-2">
          <label className="space-y-2 text-sm text-slate-300">
            <span>Title</span>
            <input
              type="text"
              {...register('title', { required: 'Title is required' })}
              className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none transition focus:border-cyan-400"
            />
            {errors.title ? <p className="text-xs text-rose-400">{errors.title.message}</p> : null}
          </label>

          <label className="space-y-2 text-sm text-slate-300">
            <span>DOI</span>
            <input
              type="text"
              {...register('doi', { required: 'DOI is required' })}
              className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none transition focus:border-cyan-400"
            />
            {errors.doi ? <p className="text-xs text-rose-400">{errors.doi.message}</p> : null}
          </label>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <label className="space-y-2 text-sm text-slate-300">
            <span>Record type</span>
            <select
              {...register('record_type', { required: 'Record type is required' })}
              className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none transition focus:border-cyan-400"
            >
              <option value="">Select type</option>
              {typeOptions.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
            {errors.record_type ? <p className="text-xs text-rose-400">{errors.record_type.message}</p> : null}
          </label>

          <label className="space-y-2 text-sm text-slate-300">
            <span>Status</span>
            <select
              {...register('status', { required: 'Status is required' })}
              className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none transition focus:border-cyan-400"
            >
              <option value="">Select status</option>
              {statusOptions.map((status) => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
            </select>
            {errors.status ? <p className="text-xs text-rose-400">{errors.status.message}</p> : null}
          </label>
        </div>

        <label className="space-y-2 text-sm text-slate-300">
          <span>License</span>
          <input
            type="text"
            {...register('license', { required: 'License is required' })}
            className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none transition focus:border-cyan-400"
          />
          {errors.license ? <p className="text-xs text-rose-400">{errors.license.message}</p> : null}
        </label>

        <label className="space-y-2 text-sm text-slate-300">
          <span>Publication date</span>
          <input
            type="date"
            {...register('publication_date')}
            className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none transition focus:border-cyan-400"
          />
        </label>

        <label className="space-y-2 text-sm text-slate-300">
          <span>Description</span>
          <textarea
            {...register('description', { required: 'Description is required' })}
            rows={5}
            className="w-full rounded-3xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none transition focus:border-cyan-400"
          />
          {errors.description ? <p className="text-xs text-rose-400">{errors.description.message}</p> : null}
        </label>

        <div className="flex flex-wrap items-center gap-3">
          <button
            type="submit"
            disabled={isSubmitting || createMutation.isPending || updateMutation.isPending}
            className="inline-flex items-center rounded-full bg-cyan-500 px-6 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {mode === 'create' ? 'Create Record' : 'Save Changes'}
          </button>
          <button
            type="button"
            onClick={() => navigate(mode === 'create' ? '/records' : `/records/${id}`)}
            className="inline-flex items-center rounded-full border border-slate-700 px-6 py-3 text-sm font-semibold text-slate-200 transition hover:border-cyan-500/40 hover:text-white"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  )
}

export default RecordForm
