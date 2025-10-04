const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export async function getPacks() {
  const res = await fetch(`${API_BASE}/packs`)
  return res.json()
}

export async function createSession(pack_slug: string, token: string) {
  const res = await fetch(`${API_BASE}/sessions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({ pack_slug }),
  })
  return res.json()
}

export async function postAnswer(id: string, key: string, raw_text: string, token: string) {
  const res = await fetch(`${API_BASE}/sessions/${id}/answer`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({ key, raw_text }),
  })
  return res.json()
}

export async function getSessionStatus(id: string, token: string) {
  const res = await fetch(`${API_BASE}/sessions/${id}`, {
    headers: { 'Authorization': `Bearer ${token}` },
  })
  return res.json()
}

export async function getMessages(id: string, token: string) {
  const res = await fetch(`${API_BASE}/sessions/${id}/messages`, {
    headers: { 'Authorization': `Bearer ${token}` },
  })
  return res.json()
}

export async function uploadDocument(id: string, kind: string, file: File, token: string) {
  const form = new FormData()
  form.append('kind', kind)
  form.append('file', file)
  const res = await fetch(`${API_BASE}/sessions/${id}/upload`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: form,
  })
  return res.json()
}

export function renderPdfUrl(id: string) {
  return `${API_BASE}/sessions/${id}/render`
}

export async function getPackNotes(slug: string) {
  const res = await fetch(`${API_BASE}/packs/${slug}/notes`)
  return res.json()
}
