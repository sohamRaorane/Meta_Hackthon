import React from 'react';
import { 
  Car, 
  Bus, 
  Train, 
  Navigation, 
  Bike, 
  ArrowLeftRight, 
  PlusCircle, 
  Clock, 
  ChevronDown, 
  X,
  Target,
  Smartphone
} from 'lucide-react';
import type { RouteData, RouteInputState, TransportType } from '../types/route';
import RouteCard from './RouteCard';

interface SidebarProps {
  inputState: RouteInputState;
  routes: RouteData[];
  selectedRouteId: string;
  bestRouteId: string;
  onSelectRoute: (id: string) => void;
  onRecalculate: () => void;
}

const transportIcons: Record<string, React.ReactNode> = {
  best: <Target size={34} />,
  auto: <Car size={34} />,
  bus: <Bus size={34} />,
  train: <Train size={34} />,
  walking: <Navigation size={34} />,
  cycling: <Bike size={34} />,
};

const Sidebar: React.FC<SidebarProps> = ({
  inputState,
  routes,
  selectedRouteId,
  bestRouteId,
  onSelectRoute,
  onRecalculate,
}) => {
  const modes: { label: string; type: string; info?: string }[] = [
    { label: 'Best', type: 'best' },
    { label: '36 min', type: 'auto' },
    { label: '26 min', type: 'bus', info: '26 min' },
    { label: '32 min', type: 'train', info: '32 min' },
    { label: '2h 5m', type: 'walking', info: '2h 5m' },
  ];

  return (
    <aside className="relative flex h-full w-full flex-col bg-white overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 pt-4">
        <div className="flex gap-4 border-b w-full pb-1">
          {modes.slice(0, 5).map((mode, i) => (
            <button key={i} className={`flex flex-col items-center pb-2 px-1 relative transition-colors ${i === 0 ? 'text-blue-600 after:absolute after:bottom-0 after:left-0 after:right-0 after:h-0.5 after:bg-blue-600' : 'text-slate-500 hover:text-slate-900'}`}>
              <div className="mb-1">{transportIcons[mode.type]}</div>
              <span className="text-[10px] font-medium">{mode.label}</span>
            </button>
          ))}
          <button className="flex items-center justify-center pb-2 text-slate-500">
            <X size={20} />
          </button>
        </div>
      </div>

      {/* Inputs */}
      <div className="relative px-4 py-4 space-y-2">
        <div className="absolute right-6 top-1/2 -translate-y-1/2 z-10">
          <button className="p-1 rounded-full border border-slate-200 bg-white shadow-sm hover:bg-slate-50">
            <ArrowLeftRight size={16} className="rotate-90 text-slate-600" />
          </button>
        </div>

        <div className="relative flex items-center gap-3">
          <div className="flex flex-col items-center gap-1 mt-1">
            <div className="h-4 w-4 rounded-full border-2 border-slate-400 bg-white" />
            <div className="w-[2px] h-10 border-l-2 border-dotted border-slate-300" />
            <div className="h-5 w-4 flex justify-center">
               <div className="w-1 h-3 rounded-full bg-slate-400" />
            </div>
          </div>
          <div className="flex-1 space-y-2">
            <div className="relative">
              <input 
                type="text" 
                defaultValue={inputState.source}
                className="w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
              />
            </div>
            <div className="relative">
              <input 
                type="text" 
                defaultValue={inputState.destination}
                className="w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
              />
            </div>
          </div>
        </div>

        <button className="flex items-center gap-2 text-sm text-slate-600 hover:text-slate-900 pt-1">
          <PlusCircle size={18} />
          <span>Add destination</span>
        </button>
      </div>

      {/* Options */}
      <div className="flex items-center justify-between border-y border-slate-100 px-6 py-4 bg-slate-50/50">
        <button className="btn-premium">
          <Clock size={16} />
          <span>Leave now</span>
          <ChevronDown size={14} className="text-slate-400" />
        </button>
        <button className="text-sm font-black text-blue-600 hover:text-blue-700 transition-colors" onClick={onRecalculate}>
          ROUTE OPTIONS
        </button>
      </div>

      {/* Route List */}
      <div className="flex-1 overflow-y-auto bg-white custom-scrollbar">
         <div className="px-6 py-3 flex items-center justify-between text-[10px] font-black uppercase tracking-widest text-blue-600 bg-blue-50/30 border-b border-blue-50">
            <div className="flex items-center gap-2">
              <Smartphone size={14} />
              <span>Send to Phone</span>
            </div>
            <button className="hover:text-blue-800 transition-colors">
              COPY LINK
            </button>
         </div>

        <div className="divide-y divide-slate-100">
          {routes.map((route) => {
            const isBest = route.id === bestRouteId;
            const isSelected = route.id === selectedRouteId;
            
            return (
              <div key={route.id} className="relative">
                {isBest && (
                  <div className="absolute left-6 top-2 z-10 rounded-full bg-emerald-500 px-2 py-0.5 text-[8px] font-black uppercase tracking-widest text-white shadow-sm">
                    Recommended
                  </div>
                )}
                <RouteCard
                  route={route}
                  selected={isSelected}
                  best={isBest}
                  onSelect={onSelectRoute}
                />
              </div>
            );
          })}
        </div>

        <div className="p-4 mt-2">
           <h3 className="text-sm font-semibold text-slate-900 mb-4">Explore nearby Kurla</h3>
           <div className="flex items-center gap-3 p-4 rounded-2xl bg-blue-50 border border-blue-100">
             <div className="p-2 rounded-full bg-white text-blue-600">
               <PlusCircle size={20} />
             </div>
             <p className="text-xs text-slate-600 leading-tight">
               New! Continue your trip, tap the notification on your phone to get directions
             </p>
             <button className="ml-auto text-slate-400">
               <X size={16} />
             </button>
           </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;

