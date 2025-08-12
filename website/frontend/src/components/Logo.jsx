import React from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

export default function Logo() {
  const { pathname, search } = useLocation()
  const navigate = useNavigate()
  const isResults = pathname === '/results' && new URLSearchParams(search).get('q')

  // Fixed for smooth transforms, now clickable to navigate home
  const baseClasses = 'fixed left-0 top-0 z-40 cursor-pointer'
  const transitionClasses = 'transition-transform duration-[500ms] ease-[cubic-bezier(0.16,1,0.3,1)] will-change-transform'

  // Keep same scale in both positions. Only translate changes.
  const style = isResults
    ? {
        transform: 'translate(24px, 16px) scale(1)',
      }
    : {
        transform: 'translate(calc(50vw - 9rem), 0vh) scale(1)',
      }

  const handleClick = () => {
    navigate('/')
  }

  return (
    <div 
      className={`${baseClasses} ${transitionClasses}`} 
      style={style}
      onClick={handleClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          handleClick()
        }
      }}
    >
      <img src={'/logo.png'} alt="BM EventGuide" className={'w-72 h-auto'} />
    </div>
  )
}


