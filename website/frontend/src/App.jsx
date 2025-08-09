import React from 'react'
export default function App({ children }) {
  return (
    <div data-theme="caramellatte" className="min-h-screen bg-base-100 text-base-content">
      <header className="bg-base-100 shadow">
        <div className="mx-auto max-w-5xl px-4 py-4">
          <h1 className="text-xl font-semibold">BM EventGuide</h1>
        </div>
      </header>
      <main className="mx-auto max-w-5xl px-4 py-6">
        {children}
      </main>
    </div>
  )
}


