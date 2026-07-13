type ToastProps = {
  title: string
  message: string
  variant?: 'success' | 'error' | 'info'
}

const Toast = ({ title, message, variant = 'info' }: ToastProps) => (
  <div
    className={`max-w-sm rounded-xl border px-4 py-3 shadow-lg transition ${
      variant === 'success'
        ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-100'
        : variant === 'error'
        ? 'border-rose-500/40 bg-rose-500/10 text-rose-100'
        : 'border-slate-500/20 bg-slate-800 text-slate-100'
    }`}
  >
    <p className="font-semibold">{title}</p>
    <p className="mt-1 text-sm text-slate-300">{message}</p>
  </div>
)

export default Toast
