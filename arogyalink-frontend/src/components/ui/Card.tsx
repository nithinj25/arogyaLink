import type { HTMLAttributes, ReactNode } from 'react'

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode
  padding?: 'none' | 'sm' | 'md' | 'lg'
  border?: boolean
}

const paddings = { none: '', sm: 'p-3', md: 'p-5', lg: 'p-7' }

export function Card({ children, padding = 'md', border = true, className = '', ...props }: CardProps) {
  return (
    <div
      className={`bg-white dark:bg-stone-900 rounded-2xl ${border ? 'border border-stone-200 dark:border-stone-800' : ''} ${paddings[padding]} ${className}`}
      {...props}
    >
      {children}
    </div>
  )
}

interface CardHeaderProps { title: string; subtitle?: string; action?: ReactNode }

export function CardHeader({ title, subtitle, action }: CardHeaderProps) {
  return (
    <div className="flex items-start justify-between gap-4 mb-4">
      <div>
        <h3 className="font-semibold text-stone-900 dark:text-white text-sm">{title}</h3>
        {subtitle && <p className="text-xs text-stone-500 mt-0.5">{subtitle}</p>}
      </div>
      {action && <div className="shrink-0">{action}</div>}
    </div>
  )
}

export default Card
