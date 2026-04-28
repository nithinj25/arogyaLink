import type { ReactNode } from 'react'

type Color = 'stone' | 'blue' | 'green' | 'yellow' | 'orange' | 'red' | 'magenta' | 'cyan'

interface BadgeProps {
  children: ReactNode
  color?: Color
  dot?: boolean
  className?: string
}

const colors: Record<Color, string> = {
  stone:   'bg-stone-100 text-stone-700 dark:bg-stone-800 dark:text-stone-300',
  blue:    'bg-blue-50 text-blue-700 border border-blue-200 dark:bg-blue-950/30 dark:text-blue-300 dark:border-blue-800',
  green:   'bg-green-50 text-green-700 border border-green-200 dark:bg-green-950/30 dark:text-green-300 dark:border-green-800',
  yellow:  'bg-amber-50 text-amber-700 border border-amber-200 dark:bg-amber-950/30 dark:text-amber-300 dark:border-amber-800',
  orange:  'bg-orange-50 text-orange-700 border border-orange-200 dark:bg-orange-950/30 dark:text-orange-300 dark:border-orange-800',
  red:     'bg-red-50 text-red-700 border border-red-200 dark:bg-red-950/30 dark:text-red-300 dark:border-red-800',
  magenta: 'bg-pink-50 text-pink-700 border border-pink-200 dark:bg-pink-950/30 dark:text-pink-300 dark:border-pink-800',
  cyan:    'bg-cyan-50 text-cyan-700 border border-cyan-200 dark:bg-cyan-950/30 dark:text-cyan-300 dark:border-cyan-800',
}

const dotColors: Record<Color, string> = {
  stone: 'bg-stone-500', blue: 'bg-blue-500', green: 'bg-green-500',
  yellow: 'bg-amber-500', orange: 'bg-orange-500', red: 'bg-red-500',
  magenta: 'bg-pink-500', cyan: 'bg-cyan-500',
}

export default function Badge({ children, color = 'stone', dot = false, className = '' }: BadgeProps) {
  return (
    <span className={`inline-flex items-center gap-1.5 text-[11px] font-medium px-2 py-0.5 rounded-full ${colors[color]} ${className}`}>
      {dot && <span className={`size-1.5 rounded-full ${dotColors[color]}`} />}
      {children}
    </span>
  )
}
