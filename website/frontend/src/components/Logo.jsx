import React from 'react'
import { useNavigate } from 'react-router-dom'

export default function Logo() {
  const navigate = useNavigate()
  // Let the logo scroll with the page on all viewports
  const baseClasses = 'pointer-events-none z-0 mx-auto md:mx-0'

  const handleClick = () => {
    navigate('/')
  }

  return (
    <div 
      className={baseClasses}
    >
      <img
        src={'/logo.png'}
        alt="BM EventGuide"
        className={'pointer-events-auto cursor-pointer w-40 md:w-72 h-auto'}
        onClick={handleClick}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault()
            handleClick()
          }
        }}
      />
    </div>
  )
}


