import { useState, useEffect } from "react"
import "./App.css"

const EXAMPLE = {
  word: "tiesitkö",
  readings: [{
    word_id: "tietää",
    root: "tie",
    segments: [
      { surface: "tie", role: "stem",   label: "root" },
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
      </div>
      {reading.word_id && (
        <div className="lemma-row">
          <span className="lemma-form">{reading.word_id}</span>
          <span className="lemma-label">dictionary form</span>
        </div>
      )}
      {segments ? (
        <div className="segments">
          {segments.map((s, j) => {
            const cumulative = segments.slice(0, j + 1).map(x => x.surface).join("")
            return (
              <div
                key={j}
                className={`step step--${s.role}${animate ? " step--animate" : ""}`}
                style={animate ? { animationDelay: `${j * 70}ms` } : {}}
              >
                <div className="step-surface">
                  {j > 0 && <span className="step-plus">+ </span>}
                  <span className="step-morph">{s.surface}</span>
                  {j > 0 && <span className="step-arrow">  →  {cumulative}</span>}
                </div>
                {s.label && <div className="step-label">{s.label}</div>}
              </div>
            )
          })}
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
