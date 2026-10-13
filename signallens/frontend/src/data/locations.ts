export interface DemoLocation {
  label: string
  latitude: number
  longitude: number
}

// Manually selected areas with known coordinates. Geocoding is a later feature.
export const DEMO_LOCATIONS: DemoLocation[] = [
  { label: 'Bengaluru, India', latitude: 12.9716, longitude: 77.5946 },
  { label: 'Mumbai, India', latitude: 19.076, longitude: 72.8777 },
  { label: 'London, United Kingdom', latitude: 51.5072, longitude: -0.1276 },
  { label: 'Singapore', latitude: 1.3521, longitude: 103.8198 },
]
