import { motion } from 'motion/react'
import { useRef, type ReactNode } from 'react'

/** Reactbits-style BlurText: characters fade + de-blur in, once. Used sparingly on titles. */
export function BlurText({ text, className }: { text: string; className?: string }) {
  const chars = Array.from(text)
  return (
    <span className={className} style={{ display: 'inline-block' }}>
      {chars.map((ch, i) => (
        <motion.span
          key={i}
          style={{ display: 'inline-block', whiteSpace: 'pre' }}
          initial={{ opacity: 0, filter: 'blur(8px)', y: 6 }}
          animate={{ opacity: 1, filter: 'blur(0px)', y: 0 }}
          transition={{ duration: 0.5, delay: Math.min(i * 0.03, 0.6), ease: 'easeOut' }}
        >
          {ch}
        </motion.span>
      ))}
    </span>
  )
}

/** Reactbits-style AnimatedContent: a block fades + rises in on mount/key change. */
export function AnimatedContent({
  children,
  reKey,
}: {
  children: ReactNode
  reKey?: string | number
}) {
  return (
    <motion.div
      key={reKey}
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
    >
      {children}
    </motion.div>
  )
}

/** Reactbits-style SpotlightCard: cursor-follow warm glow. Restrained, GPU-cheap. */
export function useSpotlight() {
  const ref = useRef<HTMLDivElement>(null)
  const onMove = (e: React.MouseEvent) => {
    const el = ref.current
    if (!el) return
    const r = el.getBoundingClientRect()
    el.style.setProperty('--mx', `${e.clientX - r.left}px`)
    el.style.setProperty('--my', `${e.clientY - r.top}px`)
  }
  return { ref, onMove }
}
