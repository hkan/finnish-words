import { useState, useEffect } from "react"
import Reading from "./Reading"

export default function ExampleDisplay({ ui, lang }) {
  const [exampleData, setExampleData] = useState(null)

  useEffect(() => {
    // Fetch real example data to ensure it matches current API structure
    fetch(`/analyse?word=tiesitkö&lang=${lang}`)
      .then(r => r.json())
      .then(data => {
        if (data.readings && data.readings.length > 0) {
          setExampleData(data.readings[0])
        }
      })
      .catch(err => console.error('Failed to load example:', err))
  }, [lang])

  if (!exampleData) {
    return (
      <div className="example-state">
        <p className="hint">…</p>
      </div>
    )
  }

  return (
    <div className="example-state">
      <p className="example-label">{ui.example}</p>
      <Reading
        reading={exampleData}
        word="tiesitkö"
        animate={false}
        ui={ui}
      />
    </div>
  )
}
