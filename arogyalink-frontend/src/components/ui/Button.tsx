import { forwardRef } from 'react'
import type { ButtonHTMLAttributes, ReactNode } from 'react'

type Variant = 'primary' | 'secondary' | 'ghost' | 'danger'
type Size    = 'sm' | 'md' | 'lg'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  size?: Size
  loading?: boolean
  icon?: ReactNode
  iconRight?: ReactNode
  fullWidth?: boolean
}

const base = 'inline-flex items-center justify-center gap-2 font-medium rounded-full transition-all duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-40 select-none'

const variants: Record<Variant, string> = {
  primary:   'bg-stone-900 text-white hover:bg-stone-700 focus-visible:ring-stone-900 dark:bg-white dark:text-stone-900 dark:hover:bg-stone-100',
  secondary: 'bg-transparent text-stone-900 border border-stone-300 hover:bg-stone-100 focus-visible:ring-stone-400 dark:text-white dark:border-stone-700 dark:hover:bg-stone-800',
  ghost:     'bg-transparent text-stone-600 hover:bg-stone-100 hover:text-stone-900 focus-visible:ring-stone-400 dark:text-stone-400 dark:hover:bg-stone-800 dark:hover:text-white',
  danger:    'bg-emergency text-white hover:bg-red-700 focus-visible:ring-emergency',
}

const sizes: Record<Size, string> = {
  sm: 'text-xs px-3.5 py-1.5 h-7',
  md: 'text-sm px-5 py-2 h-9',
  lg: 'text-sm px-7 py-2.5 h-11',
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(({
  variant = 'primary', size = 'md', loading = false,
  icon, iconRight, fullWidth = false,
  className = '', children, disabled, ...props
}, ref) => (
  <button
    ref={ref}
    disabled={disabled || loading}
    className={`${base} ${variants[variant]} ${sizes[size]} ${fullWidth ? 'w-full' : ''} ${className}`}
    {...props}
  >
    {loading
      ? <span className="size-3.5 border-2 border-current border-t-transparent rounded-full animate-spin" />
      : icon}
    {children}
    {!loading && iconRight}
  </button>
))

Button.displayName = 'Button'
export default Button
