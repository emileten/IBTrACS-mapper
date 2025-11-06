import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from './App'

// Mock react-leaflet since it requires DOM/browser environment
vi.mock('react-leaflet', () => ({
  MapContainer: ({ children }) => <div data-testid="map-container">{children}</div>,
  TileLayer: () => <div data-testid="tile-layer" />,
  Polyline: () => <div data-testid="polyline" />,
}))

// Mock Leaflet CSS import
vi.mock('leaflet/dist/leaflet.css', () => ({}))

describe('App', () => {
  beforeEach(() => {
    // Reset fetch mock before each test
    global.fetch = vi.fn()
  })

  it('should render and show 13 storms when selecting August 2025', async () => {
    const user = userEvent.setup()

    // Mock API response with 13 storms
    const mockStorms = Array.from({ length: 13 }, (_, i) => ({
      ID: `storm-${i}`,
      name: `Storm ${i}`,
      lat: [10 + i, 11 + i],
      lon: [100 + i, 101 + i],
    }))

    const mockResponse = {
      storms: mockStorms,
    }

    // Mock fetch to return successful response
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    })

    // Render the App component
    render(<App />)

    // Find the year selector by ID and change it to 2025
    const yearSelect = document.getElementById('year-select')
    expect(yearSelect).toBeInTheDocument()
    await user.selectOptions(yearSelect, '2025')

    // Find the month selector by ID and change it to August (08)
    const monthSelect = document.getElementById('month-select')
    expect(monthSelect).toBeInTheDocument()
    await user.selectOptions(monthSelect, '08')

    // Find and click the Plot button
    const plotButton = screen.getByRole('button', { name: /plot/i })
    await user.click(plotButton)

    // Wait for the API call and loading to complete
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith('/api/storms/2025/08')
    })

    // Wait for the success message to appear
    await waitFor(() => {
      const successMessage = screen.getByText(/Found 13 storms/i)
      expect(successMessage).toBeInTheDocument()
    })

    // Verify the fetch was called with the correct URL
    expect(global.fetch).toHaveBeenCalledTimes(1)
    expect(global.fetch).toHaveBeenCalledWith('/api/storms/2025/08')
  })
})

