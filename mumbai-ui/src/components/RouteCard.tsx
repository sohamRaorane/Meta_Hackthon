import React from 'react';
import { 
  Car, 
  Bus, 
  Train, 
  Navigation, 
  Bike,
  Info
} from 'lucide-react';
import type { RouteData } from '../types/route';

const transportIllustrations: Record<string, string> = {
  auto: '🛺',
  bus: '🚌',
  train: '🚆',
  walking: '🚶',
  cycling: '🚲',
  metro: '🚇',
};

// Map mode to descriptive labels from the user image
const modeInfo: Record<string, { via: string; label: string }> = {
  auto: { via: 'via NH 48', label: 'Fastest route, despite the usual traffic' },
  bus: { via: 'via SCLR', label: 'Moderate traffic' },
  metro: { via: 'via Metro L1', label: 'Punctual transit' },
  train: { via: 'via Central Line', label: 'High frequency' },
  walking: { via: 'via Pedestrian Path', label: 'Clear path' },
  cycling: { via: 'via Bike Lane', label: 'Eco-friendly' },
};

const RouteCard: React.FC<RouteCardProps> = ({ route, selected, best, onSelect }) => {
  const distance = (route.time * 0.4).toFixed(1);
  const info = modeInfo[route.transport_type] || modeInfo.auto;

  return (
    <button
      onClick={() => onSelect(route.id)}
      className={`relative w-full px-5 py-6 text-left transition-all border-l-[6px] ${
        selected 
          ? 'bg-blue-50/60 border-blue-600 shadow-inner' 
          : 'bg-white border-transparent hover:bg-slate-50'
      }`}
    >
      <div className="flex items-center justify-between gap-4">
        <div className="flex-1 space-y-1">
          <div className="flex items-center gap-2">
             <span className="text-xs font-black uppercase tracking-widest text-slate-400">
               {info.via}
             </span>
             <span className={`text-base font-black ${route.time > 35 ? 'text-orange-600' : 'text-emerald-600'}`}>
               {route.time} min
             </span>
          </div>
          
          <h4 className="text-sm font-bold text-slate-800 leading-tight">
            {info.label}
          </h4>
          
          <p className="text-xs font-bold text-slate-500">
            {distance} km
          </p>
          
          <div className="flex gap-3 pt-3">
            <button className="btn-premium px-6 !py-1.5 rounded-full">
              Details
            </button>
            <button className="btn-premium px-6 !py-1.5 rounded-full bg-slate-900 text-white hover:bg-slate-800 border-none">
              Preview
            </button>
          </div>
        </div>

        {/* Large Mode Illustration (Logo) - Enhanced */}
        <div className="flex h-28 w-36 items-center justify-center rounded-[32px] bg-slate-50 text-7xl shadow-[inset_0_2px_10px_rgba(0,0,0,0.05)] border border-slate-100 grayscale-[0.1] transition-all hover:grayscale-0 hover:scale-105">
          {transportIllustrations[route.transport_type]}
        </div>
      </div>
      
      {best && (
        <div className="absolute right-4 top-2 rounded-full bg-emerald-500/10 px-2 py-0.5 text-[8px] font-black uppercase tracking-tighter text-emerald-600 border border-emerald-500/20">
          Optimal Path
        </div>
      )}
    </button>
  );
};


export default RouteCard;

