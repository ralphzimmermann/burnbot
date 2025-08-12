import React from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

export default function Logo() {
  const { pathname, search } = useLocation()
  const navigate = useNavigate()
  const isResults = pathname === '/results' && new URLSearchParams(search).get('q')

  // Fixed on desktop, static on mobile for proper flow
  const baseClasses = 'cursor-pointer z-40 mx-auto md:mx-0 md:fixed md:top-0 md:left-0'
  const transitionClasses = 'transition-transform duration-[500ms] ease-[cubic-bezier(0.16,1,0.3,1)] will-change-transform'
  // Apply desktop-only transforms to preserve original animation/layout
  const mdTransformClass = isResults
    ? 'md:[transform:translate(24px,16px)_scale(1)]'
    : 'md:[transform:translate(calc(50vw_-_9rem),0vh)_scale(1)]'

  const handleClick = () => {
    navigate('/')
  }

  return (
    <div 
      className={`${baseClasses} ${transitionClasses} ${mdTransformClass}`}
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
      <img src={'/logo.png'} alt="BM EventGuide" className={'w-40 md:w-72 h-auto'} />
    </div>
  )
}


