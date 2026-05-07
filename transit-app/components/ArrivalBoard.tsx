"use client";
import { useEffect, useState, useCallback } from 'react';
import { Clock, X, Bus, Radio, CalendarDays } from 'lucide-react';

export default function ArrivalBoard({ stop, onClose }: { stop: any, onClose: () => void }) {
  const [arrivals, setArrivals] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchArrivals = useCallback(async () => {
    if (!stop?.stop_id) return;

    try {
      const url = `${process.env.NEXT_PUBLIC_API_URL}/v1/stations/${stop.stop_id}/arrivals`;
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      
      const data = await res.json();
      
      // Force result into an array regardless of API wrapper
      const arrivalsArray = Array.isArray(data) ? data : (data.arrivals || data.data || []);
      setArrivals(arrivalsArray);
    } catch (err) {
      console.error("Arrivals fetch failed:", err);
    } finally {
      setLoading(false);
    }
  }, [stop?.stop_id]);

  useEffect(() => {
    setLoading(true);
    fetchArrivals();
    const interval = setInterval(fetchArrivals, 20000);
    return () => clearInterval(interval);
  }, [fetchArrivals]);

  return (
    <div className="h-full bg-white flex flex-col shadow-2xl md:rounded-l-2xl overflow-hidden border-l border-gray-200">
      {/* Drag Handle for Mobile */}
      <div className="md:hidden w-12 h-1.5 bg-gray-300 rounded-full mx-auto my-3 shrink-0" />

      <div className="px-6 py-4 bg-white border-b flex justify-between items-center shrink-0">
        <div>
          <h2 className="text-xl font-bold text-gray-900 leading-tight">
            {stop?.stop_name || 'Unknown Stop'}
          </h2>
          <p className="text-sm text-gray-500 font-medium tracking-tight">Stop ID: {stop?.stop_id || 'N/A'}</p>
        </div>
        <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-full transition-colors text-gray-400 hover:text-gray-900">
          <X size={24} />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-20">
            <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4" />
            <p className="text-gray-400 text-sm animate-pulse">Updating live board...</p>
          </div>
        ) : arrivals.length > 0 ? (
          arrivals.map((arrival, i) => (
            <ArrivalItem key={`${arrival.trip_id}-${i}`} arrival={arrival} />
          ))
        ) : (
          <div className="text-center py-20 px-10">
            <CalendarDays className="mx-auto text-gray-300 mb-4" size={48} />
            <p className="text-gray-600 font-medium text-lg">No departures found</p>
            <p className="text-gray-400 text-sm mt-1">There are no more scheduled trips for this stop today.</p>
          </div>
        )}
      </div>
    </div>
  );
}

function ArrivalItem({ arrival }: { arrival: any }) {
  // --- FINAL ROBUST MAPPING ---
  // Added arrival.name to catch the key used in your Nearby JSON snippet
  const direction = 
    arrival.trip_headsign || 
    arrival.headsign || 
    arrival.destination || 
    arrival.direction_text || 
    arrival.name ||            // <--- Added this to catch the Nearby JSON key
    "Unknown Direction";

  // Check for route number variations
  const routeNum = 
    arrival.route_short_name || 
    arrival.route_id || 
    arrival.stop_code ||       // <--- Some APIs use stop_code as a fallback
    "??";

  const time = 
    arrival.arrival_time || 
    arrival.arrival || 
    arrival.time || 
    "";
  
  const minutes = calculateMinutes(time);

  return (
    <div className="flex items-center justify-between p-4 bg-white rounded-xl border border-gray-200 shadow-sm hover:border-blue-200 transition-all active:scale-[0.98]">
      <div className="flex items-center gap-4">
        {/* Route Badge */}
        <div 
          className="w-12 h-12 rounded-lg flex items-center justify-center font-black text-lg text-white shadow-inner"
          style={{ 
            backgroundColor: arrival.route_color ? `#${arrival.route_color.replace('#', '')}` : '#2563eb'
          }}
        >
          {routeNum}
        </div>
        
        <div className="min-w-0">
          <div className="font-bold text-gray-900 truncate max-w-[140px] md:max-w-[200px] text-base">
            {direction}
          </div>
          <div className="flex items-center gap-2 mt-0.5">
            {arrival.is_live ? (
              <span className="flex items-center gap-1 text-[10px] font-bold text-green-600 uppercase tracking-widest">
                <Radio size={12} className="animate-pulse" /> Live
              </span>
            ) : (
              <span className="flex items-center gap-1 text-[10px] font-bold text-gray-400 uppercase tracking-widest">
                <Clock size={12} /> Scheduled
              </span>
            )}
          </div>
        </div>
      </div>

      <div className="text-right shrink-0">
        <div className={`text-2xl font-black leading-none ${arrival.is_live ? 'text-green-600' : 'text-gray-900'}`}>
          {minutes <= 0 ? 'Due' : `${minutes}'`}
        </div>
        <div className="text-[10px] font-bold text-gray-400 mt-1.5 uppercase tabular-nums">
          {time ? time.substring(0, 5) : '--:--'}
        </div>
      </div>
    </div>
  );
}

function calculateMinutes(timeStr: string) {
  if (!timeStr || typeof timeStr !== 'string') return -999;

  const now = new Date();
  const timeParts = timeStr.split(':');
  if (timeParts.length < 2) return -999;

  const h = parseInt(timeParts[0], 10);
  const m = parseInt(timeParts[1], 10);
  const s = timeParts[2] ? parseInt(timeParts[2], 10) : 0;
  
  const arrivalDate = new Date();
  
  // Handle GTFS 24h+ format for late night trips
  if (h >= 24) {
    arrivalDate.setDate(arrivalDate.getDate() + 1);
    arrivalDate.setHours(h - 24, m, s);
  } else {
    arrivalDate.setHours(h, m, s);
  }

  const diffMs = arrivalDate.getTime() - now.getTime();
  return Math.floor(diffMs / 60000);
}