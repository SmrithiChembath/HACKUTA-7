export default function AccessibleAudio({ src }: { src?: string | null }) {
  if (!src) return null
  return (
    <audio controls src={src} aria-label="Assistant audio" className="mt-1"/>
  )
}
