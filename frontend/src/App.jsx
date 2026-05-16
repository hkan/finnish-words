import { useState, useEffect } from "react"
import "./App.css"

const EXAMPLE = {
  word: "tiesitkö",
  readings: [{
    word_id: "tietää",
    root: "tie",
    segments: [
      { surface: "tie", role: "stem",   label: null },
      { surface: "si",  role: "tense",  label: "past tense marker (-si)" },
      { surface: "t",   role: "person", label: "2nd person singular (you)" },
      { surface: "kö",  role: "clitic", label: "question particle (-kö)" },
    ],
  }],
}

function Reading({ reading, word, animate }) {
  const segments = reading.segments
  return (
    <div className="reading">
      <div className="word-header">
        <span className="word-surface">{word}</span>
        {reading.word_id && <span className="word-id">{reading.word_id}</span>}
      </div>
      {segments ? (
        <div className="segments">
          {segments.map((s, j) => (
            <div
              key={j}
              className={`chip chip--${s.role}${animate ? " chip--animate" : ""}`}
              style={animate ? { animationDelay: `${j * 70}ms` } : {}}
            >
              <span className="chip-surface">{s.surface}</span>
              {s.label && <span className="chip-roles">{s.label}</span>}
            </div>
          ))}
        </div>
      ) : (
        reading.features && (
          <div className="features-fallback">
            {Object.entries(reading.features).map(([k, v]) => (
              <span key={k} className="feature-tag">{v}</span>
            ))}
          </div>
        )
      )}
    </div>
  )
}

export default function App() {
  const params = new URLSearchParams(window.location.search)
  const queryWord = params.get("word")

  const [word, setWord] = useState(queryWord)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  // Sync word to URL query params
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    if (word.trim()) {
      params.set("word", word.trim())
    } else {
      params.delete("word")
    }
    const newUrl = `${window.location.pathname}${params.toString() ? "?" + params.toString() : ""}`
    window.history.pushState({}, "", newUrl)
  }, [word])

  async function fetchAnalysis(w) {
    setLoading(true)
    setResult(null)
    const res = await fetch(`/analyse?word=${encodeURIComponent(w)}`)
    setResult(await res.json())
    setLoading(false)
  }

  useEffect(() => {
    const trimmed = word.trim()
    if (!trimmed) { setResult(null); return }
    const timer = setTimeout(() => fetchAnalysis(trimmed), 1000)
    return () => clearTimeout(timer)
  }, [word])

  const showExample = !word.trim() && !loading

  return (
    <main>
      <header>
        <span className="app-name">Finnish Word Breakdown</span>
      </header>

      <div className="results">
        {showExample && (
          <div className="example-state">
            <p className="example-label">Example</p>
            <Reading reading={EXAMPLE.readings[0]} word={EXAMPLE.word} animate={false} />
          </div>
        )}

        {loading && <p className="hint">…</p>}

        {result && (
          result.unknown ? (
            <p className="unknown">Unknown word.</p>
          ) : (
            result.readings.map((reading, i) => (
              <Reading key={i} reading={reading} word={result.word} animate={true} />
            ))
          )
        )}
      </div>

      <div className="input-bar">
        <p className="input-hint">one Finnish word, lowercase, no punctuation</p>
        <input
          value={word}
          onChange={(e) => setWord(e.target.value)}
          placeholder="Type a Finnish word…"
          autoFocus
          autoComplete="off"
          autoCorrect="off"
          autoCapitalize="none"
          spellCheck={false}
        />
      </div>
    </main>
  )
}
