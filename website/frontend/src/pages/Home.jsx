import React from 'react'
import SearchForm from '../components/SearchForm.jsx'
import Tabs from '../components/Tabs.jsx'

export default function Home() {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-center">Find events you’ll love</h2>
      <Tabs />
      <SearchForm />
    </div>
  )
}


