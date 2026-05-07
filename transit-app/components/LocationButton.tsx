"use client";
import { useState } from 'react';
import { Compass, Loader2 } from 'lucide-react';

export default function LocationButton({ onLocationFound }: { onLocationFound: (stops: any[]) => void }) {
  const [loading, setLoading] = useState(false);

  const findMe = () => {
    setLoading(true);
    navigator.geolocation.getCurrentPosition(async (pos) => {
      try {
        const { latitude, longitude } = pos.coords;
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/v1/stations/nearby?lat=${latitude}&lon=${longitude}/`);
        const nearbyStops = await res.json();

        // Map the IDs immediately so the ArrivalBoard fetch doesn't fail
        const formattedStops = nearbyStops.map((s: any) => ({
          ...s,
          stop_id: s.id?.toString() || s.stop_code?.toString(),
          stop_name: s.name // Ensure the Hebrew name carries over
        }));

        onLocationFound(formattedStops);
      } catch (err) {
        console.error("Nearby fetch failed", err);
      } finally {
        setLoading(false);
      }
    }, () => setLoading(false));
  };

  return (
    <button 
      onClick={findMe}
      className="bg-white p-4 rounded-full shadow-xl border flex items-center justify-center text-blue-600 hover:bg-gray-50 active:scale-95 transition-all"
    >
      {loading ? <Loader2 className="animate-spin" size={24} /> : <Compass size={24} />}
    </button>
  );
}