import React from 'react'
import { useLocation } from 'react-router-dom'
import Logo from './components/Logo.jsx'
import AuthWidget from './components/AuthWidget.jsx'

export default function App({ children }) {
  const { pathname, search } = useLocation()
  const isResults = pathname === '/results' && new URLSearchParams(search).get('q')
  const isPrintRoute = pathname.startsWith('/print/')

  return (
    <div data-theme="caramellatte" className="min-h-screen bg-base-100 text-base-content">
      {!isPrintRoute && (
        <header className="bg-base-100 relative z-20">
          <div className="max-w-5xl mx-auto px-4 py-2 flex items-center justify-between pointer-events-auto">
            <Logo />
            <AuthWidget />
          </div>
        </header>
      )}
      <main
        className={[
          isPrintRoute ? 'max-w-none px-0' : 'mx-auto max-w-5xl px-4',
          'pb-6 transition-all duration-[500ms] ease-[cubic-bezier(0.16,1,0.3,1)]',
          isPrintRoute ? 'pt-0' : (isResults ? 'pt-4 md:pt-16 md:pl-72' : 'pt-6 md:pt-72'),
        ].join(' ')}
      >
        {children}
      </main>
    </div>
  )
}


