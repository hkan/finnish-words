export const GITHUB_URL = "https://github.com/hkan/finnish-words"

export const UI = {
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
  },
}

export const SUPPORTED_LANGS = Object.keys(UI)
export const DEFAULT_LANG = "en"
