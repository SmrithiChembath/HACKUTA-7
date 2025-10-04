import { useAuth0 } from '@auth0/auth0-react'
import { useEffect, useRef, useState } from 'react'
import { useParams } from 'react-router-dom'
import { getSessionStatus, postAnswer, getMessages, uploadDocument, renderPdfUrl, getPacks, getPackNotes } from '../lib/api'
import AccessibleAudio from '../components/AccessibleAudio'

export default function Chat() {
  const { sessionId } = useParams()
  const { getAccessTokenSilently } = useAuth0()
  const [messages, setMessages] = useState<any[]>([])
  const [input, setInput] = useState('')
  const [progress, setProgress] = useState(0)
  const [pendingKey, setPendingKey] = useState<string | null>(null)
  const [audioOn, setAudioOn] = useState(true)
  const [showNotes, setShowNotes] = useState(false)

  const bottomRef = useRef<HTMLDivElement>(null)

  async function refresh() {
    const token = await getAccessTokenSilently()
    const status = await getSessionStatus(sessionId!, token)
    setProgress(status.progress)
    setPendingKey(status.pending_key)
    const ms = await getMessages(sessionId!, token)
    setMessages(ms)
  }

  useEffect(() => { refresh() }, [])
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  async function send() {
    if (!input.trim() || !pendingKey) return
    const token = await getAccessTokenSilently()
    setMessages(m => [...m, { role: 'user', text: input }])
    const res = await postAnswer(sessionId!, pendingKey, input, token)
    setMessages(m => [...m, { role: 'assistant', text: res.assistant_text, audio_url: res.audio_url }])
    setInput('')
    setProgress(res.progress)
    setPendingKey(res.next_key)
  }

  async function onUpload(kind: string, file: File) {
    const token = await getAccessTokenSilently()
    const res = await uploadDocument(sessionId!, kind, file, token)
    setMessages(m => [...m, { role: 'assistant', text: res.summary }])
    await refresh()
  }

  const needIncomeProof = pendingKey === 'monthly_income'

  return (
    <div className="min-h-screen grid grid-cols-1 md:grid-cols-2">
      <div className="p-4 flex flex-col">
        <div className="banner">Guidance only; not legal advice.</div>
        <div className="flex-1 overflow-auto space-y-3 mt-3">
          {messages.map((m, idx) => (
            <div key={idx} className={m.role === 'assistant' ? 'text-left' : 'text-right'}>
              <div className={"inline-block rounded-2xl px-4 py-3 " + (m.role === 'assistant' ? 'bg-neutral-100 text-neutral-800' : 'bg-blue-600 text-white')}>
                {m.text}
              </div>
              {m.audio_url && audioOn && <AccessibleAudio src={m.audio_url} />}
            </div>
          ))}
          <div ref={bottomRef} />
        </div>
        <div className="mt-3 flex gap-2">
          <input aria-label="Type your message" className="flex-1 border rounded-lg px-3 py-2" value={input} onChange={e=>setInput(e.target.value)} onKeyDown={e=>{ if (e.key==='Enter') send() }} />
          <button className="button-primary" onClick={send}>Send</button>
          <button className="ml-2 underline" onClick={()=>setAudioOn(a=>!a)}>{audioOn ? 'Audio: On' : 'Audio: Off'}</button>
          <button className="ml-2 underline" onClick={()=>setShowNotes(true)}>Show Sources/Notes</button>
        </div>
      </div>
      <div className="p-4 border-l border-neutral-200 flex flex-col gap-3">
        <div className="font-medium">Progress</div>
        <div className="w-full bg-neutral-100 h-3 rounded-full"><div className="bg-green-600 h-3 rounded-full" style={{ width: `${progress}%` }}/></div>
        <div className="font-medium">Preview</div>
        <iframe title="PDF preview" className="border rounded-md flex-1" src={renderPdfUrl(sessionId!)} />
        {needIncomeProof && (
          <label className="block mt-2">Upload proof of income
            <input type="file" aria-label="Upload proof of income" className="mt-1" onChange={e=>{ const f=e.target.files?.[0]; if (f) onUpload('income_proof', f) }} />
          </label>
        )}
        {progress>=100 && (
          <a className="button-primary text-center" href={renderPdfUrl(sessionId!)} download>
            Download Completed Form
          </a>
        )}
      </div>

      {showNotes && (
        <NotesModal onClose={()=>setShowNotes(false)} />
      )}
    </div>
  )
}

function NotesModal({ onClose }: { onClose: ()=>void }) {
  const [notes, setNotes] = useState<any[]>([])
  useEffect(() => {
    async function load() {
      const packs = await getPacks()
      const slug = packs[0]?.slug
      const data = await getPackNotes(slug)
      setNotes(data)
    }
    load()
  }, [])

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center" role="dialog" aria-modal>
      <div className="bg-white text-black rounded-xl p-6 max-w-lg w-full">
        <div className="text-xl font-semibold mb-2">Notes</div>
        <div className="space-y-3 max-h-80 overflow-auto">
          {notes.map((n:any)=> (
            <div key={n.id} className="border rounded p-3">
              <div className="font-medium">{n.title}</div>
              <div className="text-sm text-neutral-700">{n.text}</div>
            </div>
          ))}
        </div>
        <div className="mt-4 text-right">
          <button className="underline" onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  )
}
