import { forwardRef } from 'react'
import type { InputHTMLAttributes, ReactNode } from 'react'

// Renamed from prefix/suffix to leading/trailing to avoid conflict with
// HTML's built-in prefix?: string attribute on InputHTMLAttributes
interface InputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'prefix'> {
  label?: string
  error?: string
  hint?: string
  leading?: ReactNode
  trailing?: ReactNode
  fullWidth?: boolean
}

const Input = forwardRef<HTMLInputElement, InputProps>(({
  label, error, hint, leading, trailing, fullWidth = true,
  className = '', id, ...props
}, ref) => {
  const inputId = id ?? label?.toLowerCase().replace(/\s+/g, '-')
  return (
    <div className={fullWidth ? 'w-full' : ''}>
      {label && (
        <label htmlFor={inputId} className="block text-xs font-medium text-stone-600 dark:text-stone-400 mb-1.5">
          {label}
        </label>
      )}
      <div className={`flex items-center gap-2 h-9 px-3 rounded-xl border transition-colors
        ${error
          ? 'border-emergency bg-red-50 dark:bg-red-950/20'
          : 'border-stone-200 dark:border-stone-700 bg-white dark:bg-stone-900 focus-within:border-stone-400 dark:focus-within:border-stone-500'
        }`}>
        {leading && <span className="text-stone-400 text-sm shrink-0">{leading}</span>}
        <input
          ref={ref}
          id={inputId}
          className={`flex-1 min-w-0 text-sm bg-transparent text-stone-900 dark:text-white placeholder-stone-400 outline-none ${className}`}
          {...props}
        />
        {trailing && <span className="text-stone-400 text-sm shrink-0">{trailing}</span>}
      </div>
      {error && <p className="mt-1 text-xs text-emergency">{error}</p>}
      {!error && hint && <p className="mt-1 text-xs text-stone-400">{hint}</p>}
    </div>
  )
})

Input.displayName = 'Input'

export function Textarea({ label, error, hint, fullWidth = true, className = '', id, ...props }: {
  label?: string; error?: string; hint?: string; fullWidth?: boolean; className?: string; id?: string
} & React.TextareaHTMLAttributes<HTMLTextAreaElement>) {
  const inputId = id ?? label?.toLowerCase().replace(/\s+/g, '-')
  return (
    <div className={fullWidth ? 'w-full' : ''}>
      {label && (
        <label htmlFor={inputId} className="block text-xs font-medium text-stone-600 dark:text-stone-400 mb-1.5">
          {label}
        </label>
      )}
      <textarea
        id={inputId}
        className={`w-full px-3 py-2 rounded-xl border text-sm bg-white dark:bg-stone-900 text-stone-900 dark:text-white placeholder-stone-400 outline-none transition-colors resize-none
          ${error ? 'border-emergency' : 'border-stone-200 dark:border-stone-700 focus:border-stone-400 dark:focus:border-stone-500'}
          ${className}`}
        {...props}
      />
      {error && <p className="mt-1 text-xs text-emergency">{error}</p>}
      {!error && hint && <p className="mt-1 text-xs text-stone-400">{hint}</p>}
    </div>
  )
}

export default Input
