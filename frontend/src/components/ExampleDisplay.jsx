import Reading from "./Reading"

export default function ExampleDisplay({ ui }) {
  return (
    <div className="example-state">
      <p className="example-label">{ui.example}</p>
      <Reading
        reading={{ word_id: "tietää", segments: ui.exampleSegments }}
        word="tiesitkö"
        animate={false}
        ui={ui}
      />
    </div>
  )
}
