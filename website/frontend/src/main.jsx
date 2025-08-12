import React from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'
import App from './App.jsx'
import Home from './pages/Home.jsx'
import Results from './pages/Results.jsx'
import Favorites from './pages/Favorites.jsx'
import { FavoritesProvider } from './services/favorites.jsx'
import WeekView from './pages/WeekView.jsx'

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <FavoritesProvider>
        <App>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/results" element={<Results />} />
            <Route path="/favorites" element={<Favorites />} />
            <Route path="/week" element={<WeekView />} />
          </Routes>
        </App>
      </FavoritesProvider>
    </BrowserRouter>
  </React.StrictMode>
)


