import { MapContainer, TileLayer, Polyline } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'

function Map({ storms }) {
  // Convert longitude from 0-360 range to -180-180 range
  const convertLongitude = (lon) => {
    if (lon > 180) {
      return lon - 360
    }
    return lon
  }

  // Split track into segments when crossing the date line (±180°)
  const splitTrackAtDateLine = (latArray, lonArray) => {
    const segments = []
    let currentSegment = []

    for (let i = 0; i < latArray.length; i++) {
      const convertedLon = convertLongitude(lonArray[i])
      const position = [latArray[i], convertedLon]

      // If this is the first point, add it to current segment
      if (currentSegment.length === 0) {
        currentSegment.push(position)
        continue
      }

      // Check if we've crossed the date line
      // If the longitude difference is > 180°, we've crossed
      const prevLon = currentSegment[currentSegment.length - 1][1]
      const lonDiff = Math.abs(convertedLon - prevLon)

      if (lonDiff > 180) {
        // Save current segment and start a new one
        if (currentSegment.length > 0) {
          segments.push(currentSegment)
        }
        currentSegment = [position]
      } else {
        // Continue current segment
        currentSegment.push(position)
      }
    }

    // Add the last segment
    if (currentSegment.length > 0) {
      segments.push(currentSegment)
    }

    return segments
  }

  // Generate a color for each storm (using a simple color palette)
  const getStormColor = (index) => {
    const colors = [
      '#FF0000', // Red
      '#0000FF', // Blue
      '#00FF00', // Green
      '#FF00FF', // Magenta
      '#FFFF00', // Yellow
      '#00FFFF', // Cyan
      '#FFA500', // Orange
      '#800080', // Purple
      '#FF1493', // Deep Pink
      '#00CED1', // Dark Turquoise
    ]
    return colors[index % colors.length]
  }

  return (
    <MapContainer
      center={[0, 0]}
      zoom={2}
      style={{ height: '100vh', width: '100%' }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {storms && storms.length > 0 && storms.map((storm, stormIndex) => {
        // Split track into segments at date line crossings
        const segments = splitTrackAtDateLine(storm.lat, storm.lon)
        const color = getStormColor(stormIndex)

        // Render each segment as a separate polyline
        return segments.map((segment, segmentIndex) => (
          <Polyline
            key={`${storm.ID || stormIndex}-${segmentIndex}`}
            positions={segment}
            pathOptions={{
              color: color,
              weight: 3,
              opacity: 0.8,
            }}
          />
        ))
      })}
    </MapContainer>
  )
}

export default Map

