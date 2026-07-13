import { Link } from 'react-router-dom'
import { ResearchRecord } from '../types'
import { ArrowRight, CircleDashed } from 'lucide-react'

type Props = {
  record: ResearchRecord
}

const RecordCard = ({ record }: Props) => (
  <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 transition hover:border-cyan-500/40">
    <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
      <div>
        <p className="text-xs uppercase tracking-[0.24em] text-cyan-400">{record.record_type}</p>
        <h2 className="mt-2 text-2xl font-semibold text-white">{record.title}</h2>
        <p className="mt-3 text-sm leading-6 text-slate-300">{record.description}</p>
      </div>
      <div className="flex items-center gap-2 text-sm text-slate-400">
        <CircleDashed className="h-5 w-5" />
        <span>{record.status}</span>
      </div>
    </div>

    <div className="mt-6 flex flex-wrap items-center gap-3 text-sm text-slate-400">
      <span>DOI: {record.doi}</span>
      <span>License: {record.license}</span>
      <span>{record.publication_date ?? 'No publication date'}</span>
    </div>

    <Link
      to={`/records/${record.id}`}
      className="mt-6 inline-flex items-center gap-2 rounded-full bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400"
    >
      View record
      <ArrowRight className="h-4 w-4" />
    </Link>
  </div>
)

export default RecordCard
