import { SUPPORTED_LANGS, GITHUB_URL } from "../constants/ui"

export default function Drawer({ open, onClose, ui, lang, onLangChange }) {
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
