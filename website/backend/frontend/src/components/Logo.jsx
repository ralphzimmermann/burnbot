import React from 'react'
import { useLocation } from 'react-router-dom'

export default function Logo() {
  const { pathname, search } = useLocation()
  const isResults = pathname === '/results' && new URLSearchParams(search).get('q')

  // Fixed for smooth transforms, pointer-events disabled to avoid intercepting clicks.
  const baseClasses = 'fixed left-0 top-0 z-40 pointer-events-none'
  const transitionClasses = 'transition-transform duration-[500ms] ease-[cubic-bezier(0.16,1,0.3,1)] will-change-transform'

  // Keep same scale in both positions. Only translate changes.
  const style = isResults
    ? {
        transform: 'translate(24px, 16px) scale(1)',
      }
    : {
        transform: 'translate(calc(50vw - 9rem), 0vh) scale(1)',
      }

  return (
    <div className={`${baseClasses} ${transitionClasses}`} style={style}>
      <img src={'/logo.png'} alt="BM EventGuide" className={'w-72 h-auto'} />
    </div>
  )
}


