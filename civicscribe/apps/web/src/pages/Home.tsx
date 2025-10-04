import { useAuth0 } from '@auth0/auth0-react'
import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

export default function Home() {
  const { loginWithPopup, isAuthenticated } = useAuth0()
  const nav = useNavigate()

  useEffect(() => {
    if (isAuthenticated) nav('/welcome')
  }, [isAuthenticated])

  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-6 p-6">
      <div className="banner" aria-live="polite">Guidance only; not legal advice.</div>
      <h1 className="text-4xl font-bold">CivicScribe</h1>
      <button className="button-primary" onClick={() => loginWithPopup()} aria-label="Start your application">
        Start Your Application
      </button>
    </div>
  )
}
