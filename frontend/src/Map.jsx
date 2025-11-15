import { MapContainer, TileLayer, Polyline, Popup, CircleMarker, useMap } from 'react-leaflet'
import { useState, useEffect } from 'react'
import 'leaflet/dist/leaflet.css'

// Component to update map view when storm is selected
function MapController({ bounds, zoom }) {
  const map = useMap()
  
  useEffect(() => {
    if (bounds) {
      map.fitBounds(bounds, { padding: [20, 20] })
    } else if (zoom) {
      map.setView([0, 0], 2)
    }
  }, [map, bounds, zoom])
  
  return null
}

function Map({ storms }) {
  const [selectedStorm, setSelectedStorm] = useState(null)
  const [viewMode, setViewMode] = useState('overview') // 'overview' or 'detailed'
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

  // Calculate wind-based red gradient color and opacity
  const getStormColorByWind = (windArray) => {
    // Handle case where windArray is undefined or null
    if (!windArray || !Array.isArray(windArray)) {
      return { color: '#FF0000', opacity: 0.3 }
    }
    
    // Filter out null/undefined wind values and get average
    const validWindValues = windArray.filter(wind => wind !== null && wind !== undefined && !isNaN(wind))
    if (validWindValues.length === 0) {
      // Default to minimum opacity if no wind data
      return { color: '#FF0000', opacity: 0.3 }
    }
    
    const avgWind = validWindValues.reduce((sum, wind) => sum + wind, 0) / validWindValues.length
    
    // Normalize wind speed to opacity (typical tropical cyclone range: 0-200+ kt)
    // Minimum opacity 0.3, maximum 1.0
    const minOpacity = 0.3
    const maxOpacity = 1.0
    const minWind = 0
    const maxWind = 150 // Reasonable max for visualization
    
    const normalizedWind = Math.max(0, Math.min(1, (avgWind - minWind) / (maxWind - minWind)))
    const opacity = minOpacity + (normalizedWind * (maxOpacity - minOpacity))
    
    return { color: '#FF0000', opacity }
  }

  // Format storm metadata for popup
  const formatStormPopup = (storm) => {
    // Handle missing wind data
    const windArray = storm.wind || []
    const validWindValues = windArray.filter(wind => wind !== null && wind !== undefined && !isNaN(wind))
    const avgWind = validWindValues.length > 0 ? 
      (validWindValues.reduce((sum, wind) => sum + wind, 0) / validWindValues.length).toFixed(1) : 'N/A'
    const maxWind = validWindValues.length > 0 ? Math.max(...validWindValues) : 'N/A'
    
    // Handle missing pressure data
    const pressureArray = storm.mslp || []
    const validPressureValues = pressureArray.filter(p => p !== null && p !== undefined && !isNaN(p))
    const minPressure = validPressureValues.length > 0 ? Math.min(...validPressureValues) : 'N/A'

    return `
      <div style="font-family: Arial, sans-serif; line-height: 1.4;">
        <h3 style="margin: 0 0 8px 0; color: #333;">${storm.name || 'Unnamed Storm'}</h3>
        <div><strong>ID:</strong> ${storm.ID}</div>
        <div><strong>Basin:</strong> ${storm.basin}</div>
        <div><strong>Season:</strong> ${storm.season}</div>
        <div><strong>Genesis:</strong> ${new Date(storm.genesis).toLocaleDateString()}</div>
        <div><strong>Avg Wind:</strong> ${avgWind} kt</div>
        <div><strong>Max Wind:</strong> ${maxWind} kt</div>
        <div><strong>Min Pressure:</strong> ${minPressure} hPa</div>
        <div><strong>Duration:</strong> ${storm.time ? storm.time.length : 0} observations</div>
      </div>
    `
  }

  // Handle storm click to switch to detailed view
  const handleStormClick = (storm) => {
    setSelectedStorm(storm)
    setViewMode('detailed')
  }

  // Handle back to overview
  const handleBackToOverview = () => {
    setSelectedStorm(null)
    setViewMode('overview')
  }

  // Calculate bounds for selected storm
  const getStormBounds = (storm) => {
    if (!storm || !storm.lat || !storm.lon) return null
    
    const lats = storm.lat
    const lons = storm.lon.map(convertLongitude)
    
    const minLat = Math.min(...lats)
    const maxLat = Math.max(...lats)
    const minLon = Math.min(...lons)
    const maxLon = Math.max(...lons)
    
    return [[minLat, minLon], [maxLat, maxLon]]
  }

  // Render detailed storm view
  const renderDetailedStorm = (storm) => {
    if (!storm.lat || !storm.lon || !storm.time) return null

    const segments = splitTrackAtDateLine(storm.lat, storm.lon)
    
    return (
      <>
        {/* Storm track as black line */}
        {segments.map((segment, segmentIndex) => (
          <Polyline
            key={`detailed-${storm.ID || 0}-${segmentIndex}`}
            positions={segment}
            pathOptions={{
              color: '#000000',
              weight: 2,
              opacity: 0.8,
            }}
          />
        ))}
        
        {/* Data points with wind circles */}
        {storm.lat.map((lat, index) => {
          const lon = convertLongitude(storm.lon[index])
          const wind = storm.wind && storm.wind[index] ? storm.wind[index] : 0
          const time = storm.time[index]
          const mslp = storm.mslp && storm.mslp[index] ? storm.mslp[index] : 'N/A'
          const speed = storm.speed && storm.speed[index] ? storm.speed[index] : 'N/A'
          const classification = storm.classification && storm.classification[index] ? storm.classification[index] : 'N/A'
          
          // Scale wind speed to circle radius with much more dramatic scaling
          // 0-20 kt: 3-8px, 20-50kt: 8-15px, 50-100kt: 15-25px, 100+kt: 25-40px
          let radius
          if (wind <= 20) {
            radius = 3 + (wind / 20) * 5 // 3-8px
          } else if (wind <= 50) {
            radius = 8 + ((wind - 20) / 30) * 7 // 8-15px
          } else if (wind <= 100) {
            radius = 15 + ((wind - 50) / 50) * 10 // 15-25px
          } else {
            radius = 25 + Math.min(((wind - 100) / 50) * 15, 15) // 25-40px
          }
          
          return (
            <CircleMarker
              key={`point-${index}`}
              center={[lat, lon]}
              radius={radius}
              pathOptions={{
                color: '#FF0000',
                fillColor: '#FF0000',
                fillOpacity: 0.6,
                weight: 2,
              }}
            >
              <Popup>
                <div style={{ fontFamily: 'Arial, sans-serif', lineHeight: 1.4 }}>
                  <strong>Observation #{index + 1}</strong><br/>
                  <strong>Time:</strong> {new Date(time).toLocaleString()}<br/>
                  <strong>Position:</strong> {lat.toFixed(2)}°, {lon.toFixed(2)}°<br/>
                  <strong>Wind:</strong> {wind} kt<br/>
                  <strong>Pressure:</strong> {mslp} hPa<br/>
                  <strong>Speed:</strong> {speed} kt<br/>
                  <strong>Classification:</strong> {classification}
                </div>
              </Popup>
            </CircleMarker>
          )
        })}
        
        {/* Small data point dots */}
        {storm.lat.map((lat, index) => {
          const lon = convertLongitude(storm.lon[index])
          
          return (
            <CircleMarker
              key={`dot-${index}`}
              center={[lat, lon]}
              radius={3}
              pathOptions={{
                color: '#000000',
                fillColor: '#000000',
                fillOpacity: 1,
                weight: 1,
              }}
            />
          )
        })}
      </>
    )
  }

  const stormBounds = selectedStorm ? getStormBounds(selectedStorm) : null

  return (
    <div style={{ position: 'relative', height: '100vh', width: '100%' }}>
      {/* Back button for detailed view */}
      {viewMode === 'detailed' && (
        <button
          onClick={handleBackToOverview}
          style={{
            position: 'absolute',
            top: '10px',
            left: '10px',
            zIndex: 1000,
            padding: '8px 16px',
            backgroundColor: '#fff',
            border: '2px solid #333',
            borderRadius: '4px',
            cursor: 'pointer',
            fontWeight: 'bold',
          }}
        >
          ← Back to Overview
        </button>
      )}

      {/* Storm info box for detailed view */}
      {viewMode === 'detailed' && selectedStorm && (
        <div
          style={{
            position: 'absolute',
            top: '10px',
            right: '10px',
            zIndex: 1000,
            padding: '12px',
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            border: '2px solid #333',
            borderRadius: '6px',
            maxWidth: '300px',
            fontFamily: 'Arial, sans-serif',
            fontSize: '14px',
            lineHeight: '1.4',
          }}
        >
          <h3 style={{ margin: '0 0 8px 0', color: '#333' }}>
            {selectedStorm.name || 'Unnamed Storm'}
          </h3>
          <div><strong>ID:</strong> {selectedStorm.ID}</div>
          <div><strong>Basin:</strong> {selectedStorm.basin}</div>
          <div><strong>Season:</strong> {selectedStorm.season}</div>
          <div><strong>Genesis:</strong> {new Date(selectedStorm.genesis).toLocaleDateString()}</div>
          <div><strong>Duration:</strong> {selectedStorm.time ? selectedStorm.time.length : 0} observations</div>
        </div>
      )}

      {/* Wind Speed Legend for detailed view */}
      {viewMode === 'detailed' && (
        <div
          style={{
            position: 'absolute',
            bottom: '10px',
            right: '10px',
            zIndex: 1000,
            padding: '12px',
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            border: '2px solid #333',
            borderRadius: '6px',
            fontFamily: 'Arial, sans-serif',
            fontSize: '12px',
            lineHeight: '1.4',
          }}
        >
          <h4 style={{ margin: '0 0 8px 0', color: '#333', fontSize: '14px' }}>
            Wind Speed Legend
          </h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div
                style={{
                  width: '6px',
                  height: '6px',
                  backgroundColor: '#FF0000',
                  borderRadius: '50%',
                  opacity: 0.6,
                  border: '2px solid #FF0000',
                }}
              ></div>
              <span>0-20 kt</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div
                style={{
                  width: '16px',
                  height: '16px',
                  backgroundColor: '#FF0000',
                  borderRadius: '50%',
                  opacity: 0.6,
                  border: '2px solid #FF0000',
                }}
              ></div>
              <span>20-50 kt</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div
                style={{
                  width: '30px',
                  height: '30px',
                  backgroundColor: '#FF0000',
                  borderRadius: '50%',
                  opacity: 0.6,
                  border: '2px solid #FF0000',
                }}
              ></div>
              <span>50-100 kt</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div
                style={{
                  width: '50px',
                  height: '50px',
                  backgroundColor: '#FF0000',
                  borderRadius: '50%',
                  opacity: 0.6,
                  border: '2px solid #FF0000',
                }}
              ></div>
              <span>100+ kt</span>
            </div>
          </div>
          <div style={{ marginTop: '8px', fontSize: '11px', color: '#666' }}>
            • Black dots show observation points<br/>
            • Hover circles for detailed info
          </div>
        </div>
      )}

      <MapContainer
        center={[0, 0]}
        zoom={2}
        style={{ height: '100%', width: '100%' }}
      >
        <MapController bounds={stormBounds} zoom={viewMode === 'overview'} />
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {viewMode === 'overview' && storms && storms.length > 0 && storms.map((storm, stormIndex) => {
          // Split track into segments at date line crossings
          const segments = splitTrackAtDateLine(storm.lat, storm.lon)
          const { color, opacity } = getStormColorByWind(storm.wind)

          // Render each segment as a separate polyline
          return segments.map((segment, segmentIndex) => (
            <Polyline
              key={`${storm.ID || stormIndex}-${segmentIndex}`}
              positions={segment}
              pathOptions={{
                color: color,
                weight: 2,
                opacity: opacity,
              }}
              eventHandlers={{
                mouseover: (e) => {
                  e.target.openPopup()
                },
                mouseout: (e) => {
                  e.target.closePopup()
                },
                click: () => {
                  handleStormClick(storm)
                }
              }}
            >
              <Popup>
                <div dangerouslySetInnerHTML={{ __html: formatStormPopup(storm) }} />
              </Popup>
            </Polyline>
          ))
        })}
        
        {viewMode === 'detailed' && selectedStorm && renderDetailedStorm(selectedStorm)}
      </MapContainer>
    </div>
  )
}

export default Map

