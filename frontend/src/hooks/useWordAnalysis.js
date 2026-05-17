import { useState, useEffect, useRef } from "react"
import { SUPPORTED_LANGS } from "../constants/ui"

export function useWordAnalysis(lang) {
  const initialParams = new URLSearchParams(window.location.search)
  const [word, setWord] = useState(initialParams.get("word") || "")
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  
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

  function triggerImmediateFetch() {
    fireImmediately.current = true
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
      if (!w) setResult(null)
    }
    window.addEventListener("popstate", onPop)
    return () => window.removeEventListener("popstate", onPop)
  }, [])

  return {
    word,
    result,
    loading,
    handleInputChange,
    triggerImmediateFetch,
  }
}
