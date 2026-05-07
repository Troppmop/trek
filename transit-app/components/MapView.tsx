"use client";
import { useEffect, useRef } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

interface MapViewProps {
  routeId: string | null;
  onStopClick: (stop: any) => void;
  selectedStop?: any;
}

export default function MapView({ routeId, onStopClick, selectedStop }: MapViewProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const markersRef = useRef<maplibregl.Marker[]>([]);
  const selectedMarkerRef = useRef<maplibregl.Marker | null>(null);

  // 1. INITIALIZE MAP
  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: 'https://tiles.openfreemap.org/styles/liberty',
      center: [34.817, 32.088], // Default to Israel center
      zoom: 11,
    });

    const resizeObserver = new ResizeObserver(() => map.current?.resize());
    resizeObserver.observe(mapContainer.current);

    return () => {
      resizeObserver.disconnect();
      map.current?.remove();
      map.current = null;
    };
  }, []);

  // 2. HIGHLIGHT SELECTED STOP (Nearby or Route Click)
  useEffect(() => {
    if (!map.current || !selectedStop) return;

    // Remove previous selection marker
    if (selectedMarkerRef.current) selectedMarkerRef.current.remove();

    // Map coordinates (handle both API formats)
    const lon = selectedStop.stop_lon || selectedStop.lon || selectedStop.longitude;
    const lat = selectedStop.stop_lat || selectedStop.lat || selectedStop.latitude;

    if (lon && lat) {
      const el = document.createElement('div');
      el.className = 'selected-marker';
      el.style.width = '24px';
      el.style.height = '24px';
      el.style.backgroundColor = '#ef4444'; // Red for selected
      el.style.border = '3px solid white';
      el.style.borderRadius = '50%';
      el.style.boxShadow = '0 0 15px rgba(239, 68, 68, 0.5)';

      selectedMarkerRef.current = new maplibregl.Marker({ element: el })
        .setLngLat([lon, lat])
        .addTo(map.current);

      map.current.flyTo({ center: [lon, lat], zoom: 15, duration: 2000 });
    }
  }, [selectedStop]);

  // 3. ROUTE UPDATES
  useEffect(() => {
    if (!routeId || !map.current) return;

    const updateMap = async () => {
      try {
        // Added slashes to avoid the 307 redirect error
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/v1/routes/${routeId}/geometry/`);
        if (!res.ok) return;
        const geojson = await res.json();

        // Update Route Line
        if (map.current?.getSource('route-line')) {
          (map.current.getSource('route-line') as maplibregl.GeoJSONSource).setData(geojson);
        } else {
          map.current?.addSource('route-line', { type: 'geojson', data: geojson });
          map.current?.addLayer({
            id: 'route-line',
            type: 'line',
            source: 'route-line',
            layout: { 'line-join': 'round', 'line-cap': 'round' },
            paint: { 'line-color': '#2563eb', 'line-width': 5 }
          });
        }

        // Clear markers
        markersRef.current.forEach(m => m.remove());
        markersRef.current = [];

        const stopsRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/v1/routes/${routeId}/stops/`);
        if (stopsRes.ok) {
          const stops = await stopsRes.json();
          stops.forEach((stop: any) => {
            const el = document.createElement('div');
            el.className = 'stop-marker';
            el.style.width = '12px';
            el.style.height = '12px';
            el.style.backgroundColor = 'white';
            el.style.border = '2px solid #2563eb';
            el.style.borderRadius = '50%';
            el.style.cursor = 'pointer';

            el.addEventListener('click', (e) => {
              e.preventDefault();
              e.stopPropagation();
              onStopClick(stop);
            });

            const marker = new maplibregl.Marker({ element: el, anchor: 'center' })
              .setLngLat([stop.stop_lon, stop.stop_lat])
              .addTo(map.current!);
            
            markersRef.current.push(marker);
          });
        }

        // Auto-zoom to route
        const coords = geojson.coordinates;
        if (coords.length > 0) {
          const bounds = coords.reduce((acc: any, coord: any) => acc.extend(coord), 
            new maplibregl.LngLatBounds(coords[0], coords[0]));
          map.current?.fitBounds(bounds, { padding: 80, duration: 1500 });
        }
      } catch (e) {
        console.error(e);
      }
    };

    if (map.current.isStyleLoaded()) updateMap();
    else map.current.once('style.load', updateMap);
  }, [routeId]);

  return (
    <div className="w-full h-full relative overflow-hidden bg-slate-200">
      <div ref={mapContainer} className="absolute inset-0 h-full w-full" />
    </div>
  );
}