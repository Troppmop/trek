"use client";
import { useState } from 'react';
import RouteList from '@/components/RouteList';
import MapView from '@/components/MapView';
import ArrivalBoard from '@/components/ArrivalBoard'; 
import Search from '@/components/Search';
import LocationButton from '@/components/LocationButton';

export default function Dashboard() {
  const [selectedRouteId, setSelectedRouteId] = useState<string | null>(null);
  const [selectedStop, setSelectedStop] = useState<any | null>(null);

  // Helper to handle what happens when nearby stops are found
  const handleNearbyFound = (stops: any[]) => {
    if (stops && stops.length > 0) {
      // 1. Select the first (closest) stop found
      // This will trigger the ArrivalBoard to open automatically
      setSelectedStop(stops[0]);
      
      // 2. Clear any active route highlights to focus on the stop
      setSelectedRouteId(null);
    } else {
      alert("No stops found nearby.");
    }
  };

  return (
    <main className="flex flex-col md:flex-row h-screen w-full overflow-hidden bg-gray-100 font-sans">
      
      {/* Sidebar / Bottom Sheet Container */}
      <div className={`
        z-30 bg-white shadow-2xl flex flex-col transition-all duration-300
        w-full h-[40vh] border-t order-last          /* Mobile settings */
        md:w-80 md:h-full md:border-r md:order-first  /* Desktop settings */
      `}>
        <div className="p-4 border-b space-y-4 bg-white shrink-0">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-black text-blue-600 tracking-tighter">TRANSIT.IO</h1>
            <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse"></div>
          </div>
          
          <Search onSelectResult={(stop: any) => setSelectedStop(stop)} />
        </div>

        {/* Scrollable List */}
        <div className="flex-1 overflow-y-auto min-h-0 custom-scrollbar touch-pan-y">
          <RouteList 
            onSelectRoute={(id: string) => {
              setSelectedRouteId(id);
              setSelectedStop(null);
            }} 
            selectedId={selectedRouteId} 
          />
        </div>
      </div>

      {/* Main Map Area */}
      <div className="flex-1 relative order-first md:order-none h-[60vh] md:h-full">
        <MapView 
          routeId={selectedRouteId} 
          onStopClick={(stop) => setSelectedStop(stop)}
          selectedStop={selectedStop} 
        />

        {/* Floating Actions */}
        <div className="absolute bottom-4 right-4 md:bottom-6 md:right-6 z-20 flex flex-col gap-3">
          <LocationButton onLocationFound={handleNearbyFound} />
        </div>

        {/* Arrival Board Overlay */}
        {selectedStop && (
          <div className={`
            fixed inset-0 z-50 animate-in slide-in-from-bottom duration-300    /* Mobile: Full Screen */
            md:absolute md:inset-y-0 md:right-0 md:left-auto md:w-96 md:slide-in-from-right /* Desktop: Slide Side */
          `}>
            <ArrivalBoard 
              stop={selectedStop} 
              onClose={() => setSelectedStop(null)} 
            />
          </div>
        )}
      </div>
    </main>
  );
}