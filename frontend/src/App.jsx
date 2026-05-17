import { useState, useEffect, useRef } from "react"
import "./App.css"

const GITHUB_URL = "https://github.com/hkan/finnish-words"

const UI = {
  en: {
    appName: "Finnish Word Breakdown",
    dictionaryForm: "dictionary form",
    example: "Example",
    unknownWord: "Unknown word.",
    inputHint: "one Finnish word, lowercase, no punctuation",
    placeholder: "Type a Finnish word…",
    credits: "Finnish terminology from",
    githubLabel: "See on GitHub",
    githubSub: "report issues here",
    exampleSegments: [
      { surface: "tie", role: "stem",   label: "root" },
      { surface: "si",  role: "tense",  label: "past tense marker (-si)" },
      { surface: "t",   role: "person", label: "2nd person singular (you)" },
      { surface: "kö",  role: "clitic", label: "question particle (-kö)" },
    ],
  },
  fi: {
    appName: "Sanan rakenne",
    dictionaryForm: "perusmuoto",
    example: "Esimerkki",
    unknownWord: "Tuntematon sana.",
    inputHint: "yksi suomen sana, pienillä kirjaimilla, ilman välimerkkejä",
    placeholder: "Kirjoita suomen sana…",
    credits: "Suomen kielioppitieto lähteestä",
    githubLabel: "Githubissa",
    githubSub: "ongelmat raportoidaan täällä",
    exampleSegments: [
      { surface: "tie", role: "stem",   label: "vartalo" },
      { surface: "si",  role: "tense",  label: "imperfektin tunnus (-si)" },
      { surface: "t",   role: "person", label: "2. yksikön persoona (sinä)" },
      { surface: "kö",  role: "clitic", label: "kysymysliite (-kö)" },
    ],
  },
  tr: {
    appName: "Fince Kelime Analizi",
    dictionaryForm: "sözlük biçimi",
    example: "Örnek",
    unknownWord: "Bilinmeyen kelime.",
    inputHint: "tek kelime, sadece a-z, noktalama işareti olmadan",
    placeholder: "Bir Fince kelime yazın…",
    credits: "Fince dilbilgisi terminolojisi kaynağı:",
    githubLabel: "GitHub'da görüntüle",
    githubSub: "sorunları buradan bildirin",
    exampleSegments: [
      { surface: "tie", role: "stem",   label: "kök" },
      { surface: "si",  role: "tense",  label: "geçmiş zaman eki (-si)" },
      { surface: "t",   role: "person", label: "2. tekil şahıs (sen)" },
      { surface: "kö",  role: "clitic", label: "soru ekimi (-kö)" },
    ],
  },
}

const SUPPORTED_LANGS = Object.keys(UI)
const DEFAULT_LANG = "en"

function getLangFromUrl() {
  const params = new URLSearchParams(window.location.search)
  const l = params.get("lang")
  return SUPPORTED_LANGS.includes(l) ? l : null
}

function getInitialLang() {
  return (
    getLangFromUrl() ||
    (SUPPORTED_LANGS.includes(localStorage.getItem("lang")) && localStorage.getItem("lang")) ||
    DEFAULT_LANG
  )
}

function HamburgerIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
      <rect x="2" y="5"  width="16" height="1.5" rx="0.75" fill="currentColor"/>
      <rect x="2" y="9.25" width="16" height="1.5" rx="0.75" fill="currentColor"/>
      <rect x="2" y="13.5" width="16" height="1.5" rx="0.75" fill="currentColor"/>
    </svg>
  )
}

function Drawer({ open, onClose, ui, lang, onLangChange }) {
  return (
    <>
      <div className={`drawer-backdrop${open ? " drawer-backdrop--open" : ""}`} onClick={onClose} />
      <div className={`drawer${open ? " drawer--open" : ""}`} role="dialog" aria-modal="true">
        <div className="drawer-section">
          <p className="drawer-label">Language</p>
          <div className="drawer-lang-picker">
            {SUPPORTED_LANGS.map(l => (
              <button
                key={l}
                className={`lang-btn drawer-lang-btn${lang === l ? " lang-btn--active" : ""}`}
                onClick={() => { onLangChange(l); onClose() }}
              >
                {l.toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        <div className="drawer-section">
          <p className="drawer-label">Credits</p>
          <p className="drawer-credits">
            Finnish terminology from{" "}
            <a href="https://uusikielemme.fi" target="_blank" rel="noopener noreferrer">
              uusikielemme.fi
            </a>
          </p>
          <p className="drawer-credits">
            Translations from{" "}
            <a href="https://en.wiktionary.org" target="_blank" rel="noopener noreferrer">
              Wiktionary
            </a>
            {" "}(CC BY-SA 4.0)
          </p>
        </div>

        <div className="drawer-section">
          <a
            className="drawer-github"
            href={GITHUB_URL}
            target="_blank"
            rel="noopener noreferrer"
          >
            <span className="drawer-github-label">{ui.githubLabel}</span>
            <span className="drawer-github-sub">↖ {ui.githubSub}</span>
          </a>
        </div>
      </div>
    </>
  )
}

function Reading({ reading, word, animate, ui }) {
  const segments = reading.segments
  return (
    <div className="reading">
      <div className="word-header">
        <span className="word-surface">{word}</span>
      </div>
      {reading.word_id && (
        <div className="lemma-row">
          <span className="lemma-form">{reading.word_id}</span>
          <span className="lemma-label">{ui.dictionaryForm}</span>
          {reading.translation && (
            <span className="lemma-translation">{reading.translation}</span>
          )}
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
                  {s.translation && (
                    <span 
                      className="step-translation"
                      title={s.translation_note || undefined}
                    >
                      {s.translation}
                    </span>
                  )}
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
  const [lang, setLang] = useState(getInitialLang)
  const [drawerOpen, setDrawerOpen] = useState(false)

  useEffect(() => {
    document.documentElement.lang = lang
    document.title = word.trim()
      ? `${word.trim()} – ${UI[lang].appName}`
      : UI[lang].appName
  }, [lang, word])

  useEffect(() => {
    const onKey = (e) => { if (e.key === "Escape") setDrawerOpen(false) }
    window.addEventListener("keydown", onKey)
    return () => window.removeEventListener("keydown", onKey)
  }, [])

  const ui = UI[lang] || UI[DEFAULT_LANG]

  // Set by the popstate handler so the next debounce-effect run fires the
  // request immediately rather than waiting 1s — back/forward navigation
  // represents a finalised intent, not in-progress typing.
  const fireImmediately = useRef(false)

  async function fetchAnalysis(w, l) {
    setLoading(true)
    setResult(null)
    const res = await fetch(`/analyse?word=${encodeURIComponent(w)}&lang=${l}`)
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

  function handleLangChange(l) {
    setLang(l)
    localStorage.setItem("lang", l)
    // Re-fetch current word in new language immediately
    const trimmed = word.trim()
    if (trimmed) {
      fireImmediately.current = true
    }
    // Update URL lang param
    const params = new URLSearchParams(window.location.search)
    if (l === DEFAULT_LANG) {
      params.delete("lang")
    } else {
      params.set("lang", l)
    }
    window.history.pushState({}, "", `${window.location.pathname}${params.toString() ? "?" + params : ""}`)
  }

  // Debounced fetch + URL push for non-empty input.
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
      fetchAnalysis(trimmed, lang)
    }

    if (immediate) {
      run()
      return
    }
    const timer = setTimeout(run, 1000)
    return () => clearTimeout(timer)
  }, [word, lang])

  // Back/forward: mirror URL → state.
  useEffect(() => {
    const onPop = () => {
      const params = new URLSearchParams(window.location.search)
      const w = params.get("word") || ""
      const l = params.get("lang")
      fireImmediately.current = true
      setWord(w)
      if (l && SUPPORTED_LANGS.includes(l)) setLang(l)
      if (!w) setResult(null)
    }
    window.addEventListener("popstate", onPop)
    return () => window.removeEventListener("popstate", onPop)
  }, [])

  const showExample = !word.trim() && !loading

  return (
    <main>
      <header>
        <span className="app-name">{ui.appName}</span>
        <button className="menu-btn" onClick={() => setDrawerOpen(true)} aria-label="Menu">
          <HamburgerIcon />
        </button>
      </header>

      <Drawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        ui={ui}
        lang={lang}
        onLangChange={handleLangChange}
      />

      <div className="results">
        {showExample && (
          <div className="example-state">
            <p className="example-label">{ui.example}</p>
            <Reading
              reading={{ word_id: "tietää", segments: ui.exampleSegments }}
              word="tiesitkö"
              animate={false}
              ui={ui}
            />
          </div>
        )}

        {loading && <p className="hint">…</p>}

        {result && (
          result.unknown ? (
            <p className="unknown">{ui.unknownWord}</p>
          ) : (
            result.readings.map((reading, i) => (
              <Reading key={i} reading={reading} word={result.word} animate={true} ui={ui} />
            ))
          )
        )}
      </div>

      <div className="input-bar">
        <p className="input-hint">{ui.inputHint}</p>
        <input
          value={word}
          onChange={handleInputChange}
          placeholder={ui.placeholder}
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
