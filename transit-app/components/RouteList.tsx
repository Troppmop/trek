"use client";
import { useEffect, useState } from 'react';

export default function RouteList({ onSelectRoute, selectedId }: any) {
  const [routes, setRoutes] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // 1. Remove trailing slash to avoid 307 redirects
    // 2. Add catch block to handle "Failed to fetch" errors
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/v1/routes`)
      .then(res => {
        if (!res.ok) throw new Error(`Server error: ${res.status}`);
        return res.json();
      })
      .then(data => {
        // 3. Robust check: Ensure data is an array before setting state
        if (Array.isArray(data)) {
          setRoutes(data);
        } else {
          console.error("Expected array but got:", data);
          setRoutes([]);
        }
      })
      .catch(err => {
        console.error("Fetch error:", err);
        setError(err.message);
      });
  }, []);

  if (error) {
    return <div className="p-4 text-red-500 text-sm">Error loading routes: {error}</div>;
  }

  return (
    <div className="flex flex-col">
      {/* 4. Use optional chaining or Array check to prevent .map crashes */}
      {Array.isArray(routes) && routes.length > 0 ? (
        routes.map((route: any) => (
          <button
            key={route.route_id}
            onClick={() => onSelectRoute(route.route_id)}
            className={`p-4 text-left border-b hover:bg-gray-50 transition ${
              selectedId === route.route_id ? 'bg-blue-50 border-l-4 border-l-blue-500' : ''
            }`}
          >
            <div className="flex items-center gap-3">
              <span 
                className="px-2 py-1 rounded text-xs font-bold min-w-[40px] text-center"
                style={{ 
                  backgroundColor: route.route_color ? `#${route.route_color}` : '#ccc', 
                  color: route.route_text_color ? `#${route.route_text_color}` : '#000' 
                }}
              >
                {route.route_short_name || '??'}
              </span>
              <span className="font-medium truncate text-sm">
                {route.route_long_name}
              </span>
            </div>
          </button>
        ))
      ) : (
        <div className="p-10 text-center text-gray-400 text-sm">
          {routes.length === 0 && !error ? "Loading routes..." : "No routes found"}
        </div>
      )}
    </div>
  );
}