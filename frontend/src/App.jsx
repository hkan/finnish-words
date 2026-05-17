import { useState, useEffect } from "react"
import "./App.css"
import { UI, DEFAULT_LANG } from "./constants/ui"
import { useLanguage } from "./hooks/useLanguage"
import { useWordAnalysis } from "./hooks/useWordAnalysis"
import HamburgerIcon from "./components/HamburgerIcon"
import Drawer from "./components/Drawer"
import ResultsDisplay from "./components/ResultsDisplay"
import WordInput from "./components/WordInput"

export default function App() {
  const [lang, handleLangChange] = useLanguage()
  const { word, result, loading, handleInputChange, triggerImmediateFetch } = useWordAnalysis(lang)
  const [drawerOpen, setDrawerOpen] = useState(false)

  const ui = UI[lang] || UI[DEFAULT_LANG]

  // Update document title and lang attribute
  useEffect(() => {
    document.documentElement.lang = lang
    document.title = word.trim()
      ? `${word.trim()} – ${ui.appName}`
      : ui.appName
  }, [lang, word, ui.appName])

  // Close drawer on Escape key
  useEffect(() => {
    const onKey = (e) => { if (e.key === "Escape") setDrawerOpen(false) }
    window.addEventListener("keydown", onKey)
    return () => window.removeEventListener("keydown", onKey)
  }, [])

  // Trigger immediate fetch when language changes
  useEffect(() => {
    if (word.trim()) {
      triggerImmediateFetch()
    }
  }, [lang])

  const wrappedLangChange = (l) => {
    handleLangChange(l)
  }

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
        onLangChange={wrappedLangChange}
      />

      <ResultsDisplay word={word} result={result} loading={loading} ui={ui} />

      <WordInput word={word} onChange={handleInputChange} ui={ui} />
    </main>
  )
}
