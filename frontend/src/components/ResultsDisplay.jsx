import Reading from "./Reading"
import ExampleDisplay from "./ExampleDisplay"

export default function ResultsDisplay({ word, result, loading, ui, lang }) {
  const showExample = !word.trim() && !loading

  return (
    <div className="results">
      {showExample && <ExampleDisplay ui={ui} lang={lang} />}

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
  )
}
