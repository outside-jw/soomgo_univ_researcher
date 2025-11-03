import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import ChatInterface from './components/ChatInterface'
import AdminLogin from './components/AdminLogin'
import AdminSessionList from './components/AdminSessionList'
import AdminConversationView from './components/AdminConversationView'
import ProtectedRoute from './components/ProtectedRoute'
import './App.css'

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<ChatInterface />} />
          <Route path="/admin" element={<AdminLogin />} />
          <Route
            path="/admin/sessions"
            element={
              <ProtectedRoute>
                <AdminSessionList />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/sessions/:id"
            element={
              <ProtectedRoute>
                <AdminConversationView />
              </ProtectedRoute>
            }
          />
        </Routes>
      </div>
    </Router>
  )
}

export default App
