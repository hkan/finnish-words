export default function Reading({ reading, word, animate, ui }) {
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
                    s.translation_link ? (
                      <a
                        href={s.translation_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="step-translation step-translation--link"
                        title={s.translation_note || undefined}
                      >
                        {s.translation}
                      </a>
                    ) : (
                      <span 
                        className="step-translation"
                        title={s.translation_note || undefined}
                      >
                        {s.translation}
                      </span>
                    )
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
