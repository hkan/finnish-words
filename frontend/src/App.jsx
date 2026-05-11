import { useState, useEffect } from "react"
import "./App.css"

const EXAMPLE = {
  word: "tiesitkö",
  readings: [{
    word_id: "tietää",
    morphemes: [
      { surface: "ties", roles: ["stem"] },
      { surface: "i",    roles: [] },
      { surface: "t",    roles: ["active voice", "past tense", "2nd person singular"] },
      { surface: "kö",   roles: ["question particle"] },
    ]
  }]
}

function getCategory(morpheme) {
  if (morpheme.roles.includes("stem")) return "stem"
  const role = morpheme.roles[0] || ""
  if (!role) return "unlabeled"
  if (role.includes("tense")) return "tense"
  if (role.includes("person")) return "person"
  if (role.includes("voice")) return "voice"
  if (role.includes("mood")) return "mood"
  if (role.includes("particle") || role.includes("negation")) return "clitic"
  if (role.includes("infinitive") || role.includes("participle")) return "nonfinite"
  const caseForms = ["nominative","genitive","accusative","partitive","inessive","elative",
    "illative","adessive","ablative","allative","essive","translative","instructive","abessive","comitative"]
  if (caseForms.some(c => role.includes(c))) return "case"
  if (role.includes("singular") || role.includes("plural")) return "number"
  return "other"
}

function Reading({ reading, word, animate }) {
  return (
    <div className="reading">
      <div className="word-header">
        <span className="word-surface">{word}</span>
        {reading.word_id && <span className="word-id">{reading.word_id}</span>}
      </div>
      <div className="morphemes">
        {reading.morphemes.map((m, j) => (
          <div
            key={j}
            className={`chip chip--${getCategory(m)}${animate ? " chip--animate" : ""}`}
            style={animate ? { animationDelay: `${j * 70}ms` } : {}}
          >
            <span className="chip-surface">{m.surface}</span>
            {m.roles.length > 0 && (
              <span className="chip-roles">{m.roles.join(" · ")}</span>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default function App() {
  const [word, setWord] = useState("")
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

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
