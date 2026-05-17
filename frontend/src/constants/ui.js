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

export const SUPPORTED_LANGS = Object.keys(UI)
export const DEFAULT_LANG = "en"
