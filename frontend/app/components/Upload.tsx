'use client'
/* ─────────────────────────────────────────────────────────────
   Upload.tsx — CSV uploader with file card list + preview
   Inspired by the reference modal design.
   ALL colours are hardcoded — no CSS variables.
───────────────────────────────────────────────────────────── */
import { useState, useCallback, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import dynamic from 'next/dynamic'

const Plot = dynamic(() => import('react-plotly.js'), {
  ssr: false,
})

/* ── Colour tokens (hardcoded so they always render) ─────── */
const T = {
  bg: '#080B10',       // section dark background
  card: '#FFFFFF',       // main white card
  cardBorder: '#E5E7EB',
  headingDark: '#111827',
  bodyDark: '#374151',
  mutedDark: '#6B7280',
  lightBorder: '#E5E7EB',
  dropBg: '#F9FAFB',
  dropBorder: '#D1D5DB',
  accent: '#FF6B35',
  accentLight: '#FFF1EC',
  accentBorder: '#FFD0BC',
  blue: '#3B82F6',
  blueLight: '#EFF6FF',
  green: '#10B981',
  greenLight: '#ECFDF5',
  red: '#EF4444',
  redLight: '#FEF2F2',
  rowHover: '#F9FAFB',
  pillBg: '#F3F4F6',
  pillText: '#6B7280',
  inputBg: '#F9FAFB',
  inputBorder: '#D1D5DB',
}

/* ── Types ──────────────────────────────────────────────── */
interface ColumnProfile {
  name: string
  dtype: string
  missing: number
  unique: number
  stats?: {
    mean: number | null
    median: number | null
    min: number | null
    max: number | null
  }
  top_values?: Record<string, number>
}

interface BackendProfile {
  row_count: number
  column_count: number
  columns: ColumnProfile[]
}
interface FileEntry {
  id: string          // backend file ID
  localId: string     // frontend temporary ID
  name: string
  size: string
  progress: number
  status: 'uploading' | 'done' | 'error'
  data: BackendProfile | null
}
interface QueryResult {
  question: string
  answer: string
  loading: boolean
  generated_code?: string
  plot?: any
}

/* ── Helpers ─────────────────────────────────────────────── */
function formatBytes(b: number): string {
  if (b < 1024) return `${b} B`
  if (b < 1024 * 1024) return `${(b / 1024).toFixed(1)} KB`
  return `${(b / (1024 * 1024)).toFixed(2)} MB`
}



const FAKE: Record<string, string> = {
  sum: 'The total across all numeric rows is 1,284,932 — a 12.4% increase vs the previous period average.',
  avg: 'The average value is 847.3. Median sits at 762.0, indicating a slight right skew.',
  max: 'Maximum value is 9,842 (row 1,203) — 3.2 standard deviations above the mean.',
  trend: 'Consistent upward trend of +8.3% month-over-month across the last 6 periods.',
  anomaly: '7 anomalous rows detected via z-score (threshold 2.5σ): rows 45, 203, 891, 1102, 1445, 1789, 2031.',
  default: 'Analysed the dataset for your query. The data shows interesting patterns worth exploring. Try asking about totals, averages, or anomalies.',
}
function fakeReply(q: string): string {
  const l = q.toLowerCase()
  if (/sum|total/.test(l)) return FAKE.sum
  if (/average|mean|avg/.test(l)) return FAKE.avg
  if (/max|highest|top/.test(l)) return FAKE.max
  if (/trend|growth/.test(l)) return FAKE.trend
  if (/anomal|unusual|outlier/.test(l)) return FAKE.anomaly
  return FAKE.default
}

const TYPE_COLOR: Record<string, string> = { number: T.green, text: T.blue, date: '#F59E0B' }
const TYPE_ICON: Record<string, string> = { number: '#', text: 'T', date: '⏱' }

function colType(vals: string[]): 'number' | 'text' | 'date' {
  const s = vals.filter(Boolean).slice(0, 20)
  if (!s.length) return 'text'
  if (s.filter(v => !isNaN(Number(v))).length / s.length > 0.8) return 'number'
  if (s.filter(v => !isNaN(Date.parse(v))).length / s.length > 0.7) return 'date'
  return 'text'
}


/* ═══════════════════════════════════════════════════════════
   MAIN COMPONENT
═══════════════════════════════════════════════════════════ */
export default function Upload() {
  const [files, setFiles] = useState<FileEntry[]>([])
  const [dragging, setDragging] = useState(false)
  const [activeFile, setActiveFile] = useState<FileEntry | null>(null)
  const [tab, setTab] = useState<'preview' | 'stats'>('preview')
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<QueryResult[]>([])
  const [visRows, setVisRows] = useState(10)
  const [error, setError] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)
  const [datasetInsights, setDatasetInsights] = useState<any>(null)


  /* ── Process a File object ─── */
  const processFile = useCallback(async (file: File) => {
    setError('')

    if (!file.name.match(/\.(csv|txt)$/i)) {
      setError('Please upload a .csv file')
      return
    }

    if (file.size > 20 * 1024 * 1024) {
      setError('File must be under 20 MB')
      return
    }

    const localId = Math.random().toString(36).slice(2)

    const entry: FileEntry = {
      id: '',
      localId,
      name: file.name,
      size: formatBytes(file.size),
      progress: 30,
      status: 'uploading',
      data: null,
    }

    setFiles(prev => [entry, ...prev])

    try {
      const formData = new FormData()
      formData.append('file', file)

      const res = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      })

      if (!res.ok) throw new Error('Upload failed')

      const data = await res.json()

      setDatasetInsights(data.insights)

      setFiles(prev =>
        prev.map(f =>
          f.localId === localId
            ? {
              ...f,
              id: data.id.toString(),
              progress: 100,
              status: 'done',
              data: data.profile,
            }
            : f
        )
      )

    } catch (err) {
      setFiles(prev =>
        prev.map(f =>
          f.localId === localId
            ? { ...f, status: 'error' }
            : f
        )
      )
    }

  }, [])

  const onDrop = (e: React.DragEvent) => { e.preventDefault(); setDragging(false); Array.from(e.dataTransfer.files).forEach(processFile) }
  const onInput = (e: React.ChangeEvent<HTMLInputElement>) => { Array.from(e.target.files ?? []).forEach(processFile) }

  const openPreview = (f: FileEntry) => {
    setActiveFile(f)
    setResults([])
    setVisRows(10)
  }
  const removeFile = (localId: string) => {
    setFiles(prev => prev.filter(f => f.localId !== localId))
    if (activeFile?.localId === localId) setActiveFile(null)
  }
  const submitQuery = async () => {
    if (!query.trim() || !activeFile) return

    const q = query.trim()
    setQuery('')

    setResults(prev => [
      { question: q, answer: '', loading: true },
      ...prev,
    ])

    try {
      const res = await fetch(
        `http://localhost:8000/query/${activeFile.id}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question: q }),
        }
      )

      const data = await res.json()

      setResults(prev =>
        prev.map((r, i) =>
          i === 0
            ? {
              ...r,
              answer:
                data.type === "scalar"
                  ? data.answer
                  : data.type === "table"
                    ? JSON.stringify(data.rows, null, 2)
                    : data.type === "series"
                      ? JSON.stringify(data.data, null, 2)
                      : data.answer,
              plot: data.type === "plotly" ? data.figure : null,
              loading: false,
              generated_code: data.generated_code,
            }
            : r
        )
      )

    } catch {
      setResults(prev =>
        prev.map((r, i) =>
          i === 0
            ? { ...r, answer: 'Server error.', loading: false }
            : r
        )
      )
    }
  }

  const doneCount = files.filter(f => f.status === 'done').length
  const uploadingCount = files.filter(f => f.status === 'uploading').length
  // Extracted so TypeScript knows it's non-null inside the preview panel
  const previewData: BackendProfile | null = activeFile?.data ?? null

  /* ══════════════════════════════════════════════════════════
     RENDER
  ══════════════════════════════════════════════════════════ */
  return (
    <section id="upload" style={{ padding: '100px 24px', background: T.bg, position: 'relative' }}>

      {/* Subtle glow */}
      <div style={{ position: 'absolute', top: '10%', left: '50%', transform: 'translateX(-50%)', width: '600px', height: '350px', background: 'radial-gradient(ellipse, rgba(255,107,53,0.07) 0%, transparent 70%)', pointerEvents: 'none' }} />

      <div style={{ maxWidth: '760px', margin: '0 auto', position: 'relative', zIndex: 1 }}>

        {/* Section heading */}
        <motion.div initial={{ opacity: 0, y: 28 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, margin: '-60px' }}
          style={{ textAlign: 'center', marginBottom: '40px' }}>
          <div style={{ display: 'inline-block', background: 'rgba(255,107,53,0.12)', border: '1px solid rgba(255,107,53,0.28)', padding: '5px 14px', borderRadius: '100px', marginBottom: '16px' }}>
            <span style={{ fontSize: '11px', color: T.accent, fontWeight: '700', letterSpacing: '1px', textTransform: 'uppercase', fontFamily: "'DM Sans',sans-serif" }}>Try It Now</span>
          </div>
          <h2 style={{ fontFamily: "'Syne',sans-serif", fontSize: 'clamp(28px,4vw,44px)', fontWeight: '800', letterSpacing: '-1.5px', color: '#F0F4FF', lineHeight: 1.1, marginBottom: '12px' }}>
            Upload your data &amp; ask anything
          </h2>
          <p style={{ fontFamily: "'DM Sans',sans-serif", fontSize: '15px', color: '#8892A4', fontWeight: '300', lineHeight: 1.7 }}>
            Drop a CSV file, watch it process, then ask questions in plain English.
          </p>
        </motion.div>

        {/* ── WHITE CARD ─────────────────────────────────────── */}
        <motion.div initial={{ opacity: 0, y: 24 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.5 }}
          style={{ background: T.card, borderRadius: '20px', boxShadow: '0 8px 48px rgba(0,0,0,0.22), 0 1px 0 rgba(255,255,255,0.04)', overflow: 'hidden' }}>

          {/* Card header */}
          <div style={{ padding: '28px 28px 0', borderBottom: `1px solid ${T.lightBorder}`, paddingBottom: '20px' }}>
            <h3 style={{ fontFamily: "'Syne',sans-serif", fontSize: '20px', fontWeight: '700', color: T.headingDark, marginBottom: '4px' }}>
              Upload and analyse files
            </h3>
            <p style={{ fontFamily: "'DM Sans',sans-serif", fontSize: '13px', color: T.mutedDark }}>
              Files will be parsed and ready to query instantly.
            </p>
          </div>

          <div style={{ padding: '24px 28px' }}>

            {/* ── Drop Zone ── */}
            <div
              onDragOver={e => { e.preventDefault(); setDragging(true) }}
              onDragLeave={() => setDragging(false)}
              onDrop={onDrop}
              onClick={() => inputRef.current?.click()}
              style={{
                border: `2px dashed ${dragging ? T.accent : T.dropBorder}`,
                borderRadius: '14px',
                padding: '36px 24px',
                textAlign: 'center',
                cursor: 'pointer',
                background: dragging ? T.accentLight : T.dropBg,
                transition: 'all 0.22s',
                marginBottom: '20px',
                position: 'relative',
              }}
            >
              {/* Upload icon */}
              <div style={{
                width: '60px', height: '60px', borderRadius: '16px', margin: '0 auto 14px',
                background: dragging ? 'rgba(255,107,53,0.15)' : 'rgba(255,107,53,0.08)',
                border: `1.5px solid ${dragging ? T.accent : T.accentBorder}`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                transition: 'all 0.22s',
              }}>
                <svg width="26" height="26" viewBox="0 0 24 24" fill="none">
                  <path d="M12 16V8M12 8L9 11M12 8L15 11" stroke={T.accent} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                  <path d="M20 16.5C20 18.43 18.43 20 16.5 20H7.5C5.57 20 4 18.43 4 16.5" stroke={T.accent} strokeWidth="2" strokeLinecap="round" />
                </svg>
              </div>

              <p style={{ fontFamily: "'DM Sans',sans-serif", fontSize: '15px', fontWeight: '500', color: T.bodyDark, marginBottom: '4px' }}>
                <span style={{ color: T.accent, fontWeight: '600' }}>Click to Upload</span> or drag and drop
              </p>
              <p style={{ fontFamily: "'DM Sans',sans-serif", fontSize: '12px', color: T.mutedDark }}>CSV files up to 20 MB</p>

              <input ref={inputRef} type="file" accept=".csv,.txt" multiple onChange={onInput} style={{ display: 'none' }} />
            </div>

            {/* ── Error ── */}
            <AnimatePresence>
              {error && (
                <motion.div initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                  style={{ marginBottom: '16px', padding: '10px 14px', borderRadius: '10px', background: T.redLight, border: `1px solid #FECACA`, color: T.red, fontFamily: "'DM Sans',sans-serif", fontSize: '13px' }}>
                  ⚠ {error}
                </motion.div>
              )}
            </AnimatePresence>

            {/* ── Sample buttons ── */}
            {files.length === 0 && (
              <div style={{ textAlign: 'center', marginBottom: '4px' }}>
                <p style={{ fontFamily: "'DM Sans',sans-serif", fontSize: '11px', color: T.mutedDark, marginBottom: '10px', letterSpacing: '0.5px', textTransform: 'uppercase' }}>Or try a sample</p>
                <div style={{ display: 'flex', gap: '8px', justifyContent: 'center', flexWrap: 'wrap' }}>
                  {['Sales Q3', 'HR Attrition', 'E-commerce'].map(name => (
                    <button key={name} onClick={e => {
                      e.stopPropagation()
                      const csv = `Product,Revenue,Region,Month,Units\nLaptop,48200,North,Jan,120\nPhone,32100,South,Jan,210\nTablet,21000,East,Jan,95\nLaptop,51000,West,Feb,134\nPhone,29800,North,Feb,198\nTablet,19500,South,Feb,88\nLaptop,55200,East,Mar,145\nPhone,34100,West,Mar,223\nTablet,22000,North,Mar,101\nLaptop,49800,South,Apr,128`
                      processFile(new File([csv], `${name.replace(' ', '_')}.csv`, { type: 'text/csv' }))
                    }} style={{
                      background: T.pillBg, border: `1px solid ${T.lightBorder}`,
                      borderRadius: '8px', padding: '7px 14px', cursor: 'pointer',
                      color: T.bodyDark, fontFamily: "'DM Sans',sans-serif", fontSize: '13px', fontWeight: '500',
                      transition: 'all 0.18s',
                    }}
                      onMouseEnter={e => { e.currentTarget.style.borderColor = T.accentBorder; e.currentTarget.style.color = T.accent }}
                      onMouseLeave={e => { e.currentTarget.style.borderColor = T.lightBorder; e.currentTarget.style.color = T.bodyDark }}
                    >{name}</button>
                  ))}
                </div>
              </div>
            )}

            {/* ── File list ── */}
            <AnimatePresence>
              {files.length > 0 && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ marginTop: '20px' }}>
                  <p style={{ fontFamily: "'DM Sans',sans-serif", fontSize: '13px', fontWeight: '600', color: T.bodyDark, marginBottom: '10px' }}>
                    {uploadingCount > 0 ? `${uploadingCount} file${uploadingCount > 1 ? 's' : ''} uploading…` : `${doneCount} file${doneCount !== 1 ? 's' : ''} ready`}
                  </p>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    {files.map(f => (
                      <motion.div key={f.id} layout initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                        style={{
                          border: `1px solid ${T.lightBorder}`, borderRadius: '12px', padding: '14px 16px',
                          background: '#FAFAFA', cursor: f.data ? 'pointer' : 'default',
                          boxShadow: activeFile?.id === f.id ? `0 0 0 2px ${T.accent}` : 'none',
                          transition: 'box-shadow 0.2s',
                        }}
                        onClick={() => openPreview(f)}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                          {/* Icon */}
                          <div style={{ width: '36px', height: '36px', borderRadius: '8px', flexShrink: 0, background: f.status === 'error' ? T.redLight : f.status === 'done' ? T.greenLight : T.accentLight, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '16px' }}>
                            {f.status === 'error' ? '❌' : f.status === 'done' ? '✅' : '📄'}
                          </div>
                          {/* Info */}
                          <div style={{ flex: 1, minWidth: 0 }}>
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                              <p style={{ fontFamily: "'DM Sans',sans-serif", fontSize: '14px', fontWeight: '600', color: T.headingDark, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{f.name}</p>
                              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexShrink: 0, marginLeft: '12px' }}>
                                {f.status === 'uploading' && <span style={{ fontFamily: "'DM Sans',sans-serif", fontSize: '13px', fontWeight: '600', color: T.accent }}>{Math.round(f.progress)}%</span>}
                                {f.status === 'done' && <span style={{ fontFamily: "'DM Sans',sans-serif", fontSize: '11px', color: T.green, fontWeight: '600' }}>Completed</span>}
                                <button onClick={e => { e.stopPropagation(); removeFile(f.localId) }}
                                  style={{ background: 'none', border: 'none', cursor: 'pointer', color: T.mutedDark, fontSize: '14px', padding: '2px', lineHeight: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                  {f.status === 'done' ? '🗑' : '✕'}
                                </button>
                              </div>
                            </div>
                            <p style={{ fontFamily: "'DM Sans',sans-serif", fontSize: '12px', color: T.mutedDark, marginBottom: f.status === 'uploading' ? '8px' : '0' }}>
                              {f.size}
                              {f.data
                                ? ` · ${f.data.row_count} rows · ${f.data.column_count} cols`
                                : f.status === 'uploading'
                                  ? ' · uploading…'
                                  : ''}
                            </p>
                            {/* Progress bar */}
                            {f.status === 'uploading' && (
                              <div style={{ height: '4px', background: '#E5E7EB', borderRadius: '2px', overflow: 'hidden' }}>
                                <motion.div animate={{ width: `${f.progress}%` }} transition={{ duration: 0.15 }}
                                  style={{ height: '100%', background: `linear-gradient(90deg,${T.accent},#FFB347)`, borderRadius: '2px' }} />
                              </div>
                            )}
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>

                  {/* Action buttons */}
                  <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
                    <button onClick={() => { setFiles([]); setActiveFile(null); setResults([]) }}
                      style={{ flex: 1, padding: '12px', border: `1px solid ${T.lightBorder}`, borderRadius: '10px', background: 'white', cursor: 'pointer', fontFamily: "'DM Sans',sans-serif", fontSize: '14px', fontWeight: '500', color: T.bodyDark, transition: 'all 0.18s' }}
                      onMouseEnter={e => e.currentTarget.style.borderColor = T.accent}
                      onMouseLeave={e => e.currentTarget.style.borderColor = T.lightBorder}
                    >Clear All</button>
                    <button
                      onClick={() => { const done = files.find(f => f.data); if (done) openPreview(done) }}
                      disabled={doneCount === 0}
                      style={{ flex: 2, padding: '12px', border: 'none', borderRadius: '10px', background: doneCount > 0 ? `linear-gradient(135deg,${T.accent},#FF8C61)` : '#E5E7EB', cursor: doneCount > 0 ? 'pointer' : 'default', fontFamily: "'DM Sans',sans-serif", fontSize: '14px', fontWeight: '600', color: doneCount > 0 ? 'white' : T.mutedDark, boxShadow: doneCount > 0 ? '0 4px 14px rgba(255,107,53,0.3)' : 'none', transition: 'all 0.2s' }}
                    >Analyse Files →</button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </motion.div>

        {/* ── DATA PREVIEW PANEL ──────────────────────────────── */}
        <AnimatePresence>
          {previewData && (
            <motion.div
              key="preview-panel"
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 12 }}
              transition={{ duration: 0.4 }}
              style={{ marginTop: '24px', background: T.card, borderRadius: '20px', boxShadow: '0 8px 48px rgba(0,0,0,0.22)', overflow: 'hidden' }}
            >
              {/* Panel header */}
              <div style={{ padding: '20px 24px', borderBottom: `1px solid ${T.lightBorder}`, display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '10px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{ fontSize: '20px' }}>📊</span>
                  <div>
                    <p style={{ fontFamily: "'Syne',sans-serif", fontWeight: '700', fontSize: '15px', color: T.headingDark }}>
                      {activeFile?.name}
                    </p>                    <p style={{ fontFamily: "'DM Sans',sans-serif", fontSize: '12px', color: T.mutedDark }}>
                      {previewData.row_count.toLocaleString()} rows · {previewData.column_count} cols
                    </p>
                  </div>
                </div>
                <button onClick={() => setActiveFile(null)}
                  style={{ background: 'none', border: `1px solid ${T.lightBorder}`, borderRadius: '8px', padding: '6px 14px', cursor: 'pointer', color: T.mutedDark, fontFamily: "'DM Sans',sans-serif", fontSize: '13px' }}>
                  Close ✕
                </button>
              </div>

              {/* Tabs */}
              <div style={{ display: 'flex', gap: '4px', padding: '12px 24px 0', borderBottom: `1px solid ${T.lightBorder}` }}>
                {(['preview', 'stats'] as const).map(t => (
                  <button key={t} onClick={() => setTab(t)} style={{
                    padding: '8px 18px', borderRadius: '8px 8px 0 0', border: 'none', cursor: 'pointer',
                    background: tab === t ? T.accentLight : 'transparent',
                    color: tab === t ? T.accent : T.mutedDark,
                    fontFamily: "'DM Sans',sans-serif", fontSize: '13px', fontWeight: '600',
                    borderBottom: tab === t ? `2px solid ${T.accent}` : '2px solid transparent',
                    transition: 'all 0.18s',
                  }}>{t === 'preview' ? '📋 Preview' : '📊 Column Stats'}</button>
                ))}
              </div>

              <div style={{ padding: '20px 24px' }}>

                {/* Preview table */}
                {tab === 'preview' && (
                  <div style={{ padding: '20px', textAlign: 'center', color: T.mutedDark }}>
                    Row preview will be enabled in next phase.
                  </div>
                )}

                {/* Stats grid */}
                {tab === 'stats' && (
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(160px,1fr))', gap: '12px' }}>
                    {previewData.columns.map((col: any, ci: number) => (
                      <motion.div
                        key={ci}
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: ci * 0.04 }}
                        style={{
                          border: `1px solid ${T.lightBorder}`,
                          borderRadius: '10px',
                          padding: '14px',
                          background: '#FAFAFA'
                        }}
                      >
                        <div style={{ marginBottom: '8px' }}>
                          <span style={{
                            fontFamily: "'DM Sans',sans-serif",
                            fontSize: '12px',
                            fontWeight: '600',
                            color: T.headingDark
                          }}>
                            {col.name}
                          </span>
                        </div>

                        <div style={{ fontSize: '11px', color: T.mutedDark }}>
                          <div>Type: {col.dtype}</div>
                          <div>Unique: {col.unique}</div>
                          <div>Missing: {col.missing}</div>

                          {col.stats && (
                            <>
                              <div>Mean: {col.stats.mean?.toFixed?.(2)}</div>
                              <div>Min: {col.stats.min}</div>
                              <div>Max: {col.stats.max}</div>
                            </>
                          )}
                        </div>
                      </motion.div>
                    ))}
                  </div>
                )}

                {datasetInsights && (
                  <div
                    style={{
                      marginTop: '20px',
                      background: '#FAFAFA',
                      border: `1px solid ${T.lightBorder}`,
                      borderRadius: '12px',
                      padding: '18px'
                    }}
                  >
                    <p style={{
                      fontSize: '12px',
                      fontWeight: 700,
                      color: T.mutedDark,
                      marginBottom: '10px',
                      textTransform: 'uppercase',
                      letterSpacing: '0.5px'
                    }}>
                      ✦ AI Dataset Overview
                    </p>

                    {datasetInsights.executive_summary && (
                      <div style={{
                        marginTop: '14px',
                        padding: '12px',
                        background: '#111',
                        color: '#E0E0E0',
                        borderRadius: '10px',
                        fontSize: '13px',
                        lineHeight: 1.6
                      }}>
                        <strong style={{ color: '#00FFB3' }}>Executive Summary:</strong>
                        <p style={{ marginTop: '6px' }}>
                          {datasetInsights.executive_summary}
                        </p>
                      </div>
                    )}

                    <p style={{
                      fontSize: '13px',
                      marginBottom: '10px',
                      fontFamily: "'DM Sans',sans-serif"
                    }}>
                      {datasetInsights?.overview?.rows} rows · {datasetInsights?.overview?.columns} columns
                    </p>

                    {datasetInsights?.key_findings?.map((f: string, i: number) => (
                      <div key={i}
                        style={{
                          fontSize: '13px',
                          marginBottom: '4px',
                          fontFamily: "'DM Sans',sans-serif"
                        }}
                      >
                        • {f}
                      </div>
                    ))}

                    <div style={{ marginTop: '12px' }}>
                      <strong style={{ fontSize: '13px' }}>
                        Suggested Questions:
                      </strong>

                      {datasetInsights?.suggested_questions?.map((q: string, i: number) => (
                        <div
                          key={i}
                          style={{
                            cursor: 'pointer',
                            color: T.accent,
                            marginTop: '4px',
                            fontSize: '13px'
                          }}
                          onClick={() => setQuery(q)}
                        >
                          → {q}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* ── Query box ── */}
                <div style={{ marginTop: '20px', border: `1px solid ${T.lightBorder}`, borderRadius: '12px', padding: '18px', background: '#FAFAFA' }}>
                  <p style={{ fontFamily: "'DM Sans',sans-serif", fontSize: '12px', fontWeight: '700', color: T.mutedDark, marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                    ✦ Ask about this dataset
                  </p>

                  {/* Chips */}
                  <div style={{ display: 'flex', gap: '7px', flexWrap: 'wrap', marginBottom: '12px' }}>
                    {['Total revenue?', 'Average per category', 'Find anomalies', 'Top 5 rows?'].map(p => (
                      <button key={p} onClick={() => setQuery(p)} style={{
                        background: T.accentLight, border: `1px solid ${T.accentBorder}`,
                        borderRadius: '100px', padding: '4px 12px', cursor: 'pointer',
                        color: T.accent, fontFamily: "'DM Sans',sans-serif", fontSize: '12px', fontWeight: '500',
                        transition: 'background 0.15s',
                      }}
                        onMouseEnter={e => e.currentTarget.style.background = '#FFE4D6'}
                        onMouseLeave={e => e.currentTarget.style.background = T.accentLight}
                      >{p}</button>
                    ))}
                  </div>

                  {/* Input */}
                  <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                    <input value={query} onChange={e => setQuery(e.target.value)} onKeyDown={e => e.key === 'Enter' && submitQuery()}
                      placeholder="e.g. Which product had the highest revenue?"
                      style={{ flex: 1, background: 'white', border: `1px solid ${T.inputBorder}`, borderRadius: '9px', padding: '10px 14px', color: T.headingDark, fontFamily: "'DM Sans',sans-serif", fontSize: '14px', outline: 'none', transition: 'border-color 0.18s' }}
                      onFocus={e => e.target.style.borderColor = T.accent}
                      onBlur={e => e.target.style.borderColor = T.inputBorder}
                    />
                    <button onClick={submitQuery} disabled={!query.trim()} style={{
                      background: query.trim() ? `linear-gradient(135deg,${T.accent},#FF8C61)` : '#E5E7EB',
                      border: 'none', borderRadius: '9px', width: '42px', height: '42px',
                      cursor: query.trim() ? 'pointer' : 'default', display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontSize: '17px', color: 'white', flexShrink: 0, transition: 'all 0.2s',
                      boxShadow: query.trim() ? '0 4px 12px rgba(255,107,53,0.28)' : 'none',
                    }}>→</button>
                  </div>

                  {/* Results */}
                  <AnimatePresence>
                    {results.length > 0 && (
                      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ marginTop: '14px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                        {results.map((r, i) => (
                          <motion.div key={i} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                            {/* User */}
                            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                              <div style={{ maxWidth: '75%', padding: '9px 13px', background: `linear-gradient(135deg,${T.accent},#FF8C61)`, borderRadius: '11px 11px 3px 11px', fontSize: '13px', color: 'white', fontFamily: "'DM Sans',sans-serif", lineHeight: 1.5 }}>{r.question}</div>
                            </div>
                            {/* AI */}
                            <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-start' }}>
                              <div style={{ width: '28px', height: '28px', borderRadius: '7px', flexShrink: 0, background: `linear-gradient(135deg,${T.accent},#FFB347)`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '11px', fontWeight: '800', color: 'white', fontFamily: "'Syne',sans-serif" }}>D</div>
                              <div style={{ flex: 1, padding: '10px 13px', background: 'white', border: `1px solid ${T.lightBorder}`, borderRadius: '3px 11px 11px 11px' }}>
                                <p style={{ fontSize: '10px', color: T.accent, fontWeight: '700', letterSpacing: '1px', marginBottom: '5px', fontFamily: "'DM Sans',sans-serif" }}>✦ DATALYZE AI</p>
                                {r.loading ? (
                                  <div style={{ display: 'flex', gap: '4px' }}>
                                    {[0, 1, 2].map(j => (
                                      <motion.div key={j} animate={{ y: [0, -4, 0] }} transition={{ repeat: Infinity, duration: 0.7, delay: j * 0.15 }}
                                        style={{ width: '5px', height: '5px', borderRadius: '50%', background: T.accent }} />
                                    ))}
                                  </div>
                                ) : (
                                  <>
                                    <p
                                      style={{
                                        fontSize: '13px',
                                        color: T.bodyDark,
                                        fontFamily: "'DM Sans',sans-serif",
                                        lineHeight: 1.7
                                      }}
                                    >
                                      {r.answer}
                                    </p>

                                    {r.plot && (
                                      <div style={{ marginTop: '12px' }}>
                                        <Plot
                                          {...JSON.parse(r.plot)}
                                          style={{ width: '100%' }}
                                        />
                                      </div>
                                    )}

                                    {r.generated_code && (
                                      <pre
                                        style={{
                                          marginTop: '8px',
                                          background: '#111',
                                          color: '#00FFB3',
                                          padding: '10px',
                                          borderRadius: '8px',
                                          fontSize: '11px',
                                          overflowX: 'auto'
                                        }}
                                      >
                                        {r.generated_code}
                                      </pre>
                                    )}
                                  </>
                                )
                                }
                              </div>
                            </div>
                          </motion.div>
                        ))}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

      </div>
    </section>
  )
}