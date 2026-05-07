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

  // 1. INITIALIZE MAP
  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: 'https://tiles.openfreemap.org/styles/liberty',
      center: [34.8, 32.0],
      zoom: 9,
    });

    const resizeObserver = new ResizeObserver(() => map.current?.resize());
    resizeObserver.observe(mapContainer.current);

    return () => {
      resizeObserver.disconnect();
      map.current?.remove();
      map.current = null;
    };
  }, []);

  // 2. DATA UPDATES
  useEffect(() => {
    if (!routeId || !map.current) return;

    const updateMap = async () => {
      try {
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
            paint: { 'line-color': '#ff4400', 'line-width': 5 }
          });
        }

        // --- FIXED MARKER LOGIC ---
        // 1. Clear markers from map and memory
        markersRef.current.forEach(m => m.remove());
        markersRef.current = [];

        const stopsRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/v1/routes/${routeId}/stops/`);
        if (stopsRes.ok) {
          const stops = await stopsRes.json();
          stops.forEach((stop: any) => {
            const el = document.createElement('div');
            
            // Fix: Explicitly prevent marker from capturing global drag events
            el.className = 'stop-marker';
            el.style.width = '16px';
            el.style.height = '16px';
            el.style.backgroundColor = 'white';
            el.style.border = '2px solid #2563eb'; // blue-600
            el.style.borderRadius = '50%';
            el.style.cursor = 'pointer';
            el.style.boxShadow = '0 2px 4px rgba(0,0,0,0.2)';

            // Fix Click/Teleport: Stop propagation and prevent default map behavior
            el.addEventListener('click', (e) => {
              e.preventDefault();
              e.stopPropagation();
              onStopClick(stop);
            });

            // Fix Teleport: Explicitly set anchor to center
            const marker = new maplibregl.Marker({ 
                element: el, 
                anchor: 'center' 
            })
              .setLngLat([stop.stop_lon, stop.stop_lat])
              .addTo(map.current!);
            
            markersRef.current.push(marker);
          });
        }

        // Auto-zoom
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