export default function WordInput({ word, onChange, ui }) {
  return (
    <div className="input-bar">
      <p className="input-hint">{ui.inputHint}</p>
      <input
        value={word}
        onChange={onChange}
        placeholder={ui.placeholder}
        autoFocus
        autoComplete="off"
        autoCorrect="off"
        autoCapitalize="none"
        spellCheck={false}
      />
    </div>
  )
}
