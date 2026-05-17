import { useState, useEffect } from "react"
import { SUPPORTED_LANGS, DEFAULT_LANG } from "../constants/ui"

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

export function useLanguage() {
  const [lang, setLang] = useState(getInitialLang)

  const handleLangChange = (l) => {
    setLang(l)
    localStorage.setItem("lang", l)
    
    // Update URL lang param
    const params = new URLSearchParams(window.location.search)
    if (l === DEFAULT_LANG) {
      params.delete("lang")
    } else {
      params.set("lang", l)
    }
    window.history.pushState({}, "", `${window.location.pathname}${params.toString() ? "?" + params : ""}`)
  }

  return [lang, handleLangChange]
}
