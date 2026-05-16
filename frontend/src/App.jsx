import { useState, useEffect, useRef } from "react"
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
  const initialParams = new URLSearchParams(window.location.search)
  const [word, setWord] = useState(initialParams.get("word") || "")
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  // Set by the popstate handler so the next debounce-effect run fires the
  // request immediately rather than waiting 1s — back/forward navigation
  // represents a finalised intent, not in-progress typing.
  const fireImmediately = useRef(false)

  async function fetchAnalysis(w) {
    setLoading(true)
    setResult(null)
    const res = await fetch(`/analyse?word=${encodeURIComponent(w)}`)
    setResult(await res.json())
    setLoading(false)
  }

  function clearWordUrl() {
    const params = new URLSearchParams(window.location.search)
    if (params.has("word")) {
      params.delete("word")
      const url = `${window.location.pathname}${params.toString() ? "?" + params : ""}`
      window.history.pushState({}, "", url)
    }
  }

  function handleInputChange(e) {
    const v = e.target.value
    setWord(v)
    if (!v.trim()) {
      setResult(null)
      clearWordUrl()
    }
  }

  // Debounced fetch + URL push for non-empty input. Empty-state cleanup is
  // handled directly in the input/popstate handlers so this effect only
  // synchronises external systems (history API + fetch).
  useEffect(() => {
    const trimmed = word.trim()
    if (!trimmed) return
    const immediate = fireImmediately.current
    fireImmediately.current = false

    const run = () => {
      const params = new URLSearchParams(window.location.search)
      if (params.get("word") !== trimmed) {
        params.set("word", trimmed)
        window.history.pushState({}, "", `${window.location.pathname}?${params}`)
      }
      fetchAnalysis(trimmed)
    }

    if (immediate) {
      run()
      return
    }
    const timer = setTimeout(run, 1000)
    return () => clearTimeout(timer)
  }, [word])

  // Back/forward: mirror URL → state. Flag the next fetch to skip the
  // 1s debounce since the URL change is finalised intent, not typing.
  useEffect(() => {
    const onPop = () => {
      const params = new URLSearchParams(window.location.search)
      const w = params.get("word") || ""
      fireImmediately.current = true
      setWord(w)
      if (!w) setResult(null)
    }
    window.addEventListener("popstate", onPop)
    return () => window.removeEventListener("popstate", onPop)
  }, [])

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
          onChange={handleInputChange}
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
