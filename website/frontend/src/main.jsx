import React from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'
import App from './App.jsx'
import Home from './pages/Home.jsx'
import Results from './pages/Results.jsx'
import Favorites from './pages/Favorites.jsx'
import { FavoritesProvider } from './services/favorites.jsx'
import { AuthProvider } from './services/auth.jsx'
import WeekView from './pages/WeekView.jsx'
import PrintDay from './pages/PrintDay.jsx'

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <FavoritesProvider>
          <App>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/results" element={<Results />} />
              <Route path="/favorites" element={<Favorites />} />
              <Route path="/week" element={<WeekView />} />
              <Route path="/print/day/:date" element={<PrintDay />} />
            </Routes>
          </App>
        </FavoritesProvider>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
)


