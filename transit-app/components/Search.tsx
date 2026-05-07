"use client";
import { useState } from 'react';
import { Search as SearchIcon } from 'lucide-react';

export default function Search({ onSelectResult }: any) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);

  const handleSearch = async (val: string) => {
    setQuery(val);
    if (val.length < 2) return setResults([]);
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/v1/search?q=${val}`);
    setResults(await res.json());
  };

  return (
    <div className="relative w-full max-w-md">
      <div className="flex items-center bg-white rounded-lg shadow-md border px-3 py-2">
        <SearchIcon size={18} className="text-gray-400 mr-2" />
        <input 
          className="outline-none w-full text-sm"
          placeholder="Search for a stop..."
          value={query}
          onChange={(e) => handleSearch(e.target.value)}
        />
      </div>
      {results.length > 0 && (
        <div className="absolute top-12 w-full bg-white border rounded-lg shadow-xl z-50 overflow-hidden">
          {results.map((stop: any) => (
            <div 
              key={stop.stop_id}
              onClick={() => { onSelectResult(stop); setResults([]); setQuery(""); }}
              className="p-3 hover:bg-blue-50 cursor-pointer border-b last:border-0 text-sm"
            >
              {stop.stop_name}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}