import { useAuth0 } from '@auth0/auth0-react'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getPacks, createSession } from '../lib/api'

export default function Welcome() {
  const { isAuthenticated, getAccessTokenSilently, user } = useAuth0()
  const [packs, setPacks] = useState<{slug:string,title:string}[]>([])
  const nav = useNavigate()

  useEffect(() => {
    getPacks().then(setPacks)
  }, [])

  async function startPack(slug: string) {
    const token = await getAccessTokenSilently()
    const { session_id } = await createSession(slug, token)
    nav(`/chat/${session_id}`)
  }

  if (!isAuthenticated) return (
    <div className="min-h-screen flex items-center justify-center"><div>Please sign in from the home page.</div></div>
  )

  return (
    <div className="min-h-screen p-6">
      <div className="banner">Guidance only; not legal advice.</div>
      <h2 className="text-2xl font-semibold my-4">Welcome{user?.given_name ? `, ${user.given_name}` : ''}</h2>
      <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3">
        {packs.map(p => (
          <div key={p.slug} className="card">
            <div className="text-lg font-medium mb-2">{p.title}</div>
            <button className="button-primary" onClick={() => startPack(p.slug)} aria-label={`Start ${p.title}`}>Begin</button>
          </div>
        ))}
      </div>
    </div>
  )
}
