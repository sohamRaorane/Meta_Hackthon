import React from 'react';
import { 
  Car, 
  Bus, 
  Train, 
  Navigation, 
  Bike, 
  ArrowLeft,
  X,
  Target,
  Bot,
  CloudRain,
  Sun,
  Banknote,
  Timer
} from 'lucide-react';
import type { RouteData, RouteInputState } from '../types/route';
import RouteCard from './RouteCard';

interface SidebarProps {
  inputState: RouteInputState;
  routes: RouteData[];
  selectedRouteId: string;
  bestRouteId: string;
  onSelectRoute: (id: string) => void;
  onRecalculate: () => void;
  agentPhase?: 'analyzing' | 'highlighted' | 'decided';
  taskName?: string;
  taskMeta?: any;
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
  agentPhase = 'decided',
  taskMeta = {
    weather: 'clear',
    legs: ['Origin → Dest'],
    disruptions: [],
    timeLimit: 60,
    budget: 100,
    difficulty: 'Easy'
  }
}) => {
  const modes: { label: string; type: string; info?: string }[] = [
    { label: 'Best', type: 'best' },
    { label: '36 min', type: 'auto' },
    { label: '26 min', type: 'bus', info: '26 min' },
    { label: '32 min', type: 'train', info: '32 min' },
    { label: '2h 5m', type: 'walking', info: '2h 5m' },
  ];

  const bestRoute = routes.find(r => r.id === bestRouteId);
  const usedMode = bestRoute?.transport_type || 'auto';
  const allModes = ['auto', 'bus', 'metro', 'train', 'walking', 'cycling'];
  const doNotUseModes = allModes.filter(m => m !== usedMode && routes.some(r => r.transport_type === m));

  const renderAnalyzingPhase = () => (
    <div className="flex-1 p-6 space-y-6">
      <div className="flex items-center gap-2 mb-4">
        <Bot size={24} className="text-purple-600 animate-[pulse-glow_2s_infinite]" />
        <h2 className="text-xl font-bold font-['Space_Grotesk']">AI Agent Analyzing Route...</h2>
      </div>
      
      <div className="space-y-4">
        <div className="flex flex-wrap gap-2">
           <span className="inline-flex items-center gap-1 bg-slate-100 text-slate-700 px-3 py-1 rounded-full text-xs font-bold uppercase">
             {taskMeta.weather === 'clear' ? <Sun size={14} /> : <CloudRain size={14} />} 
             {taskMeta.weather.replace('_', ' ')}
           </span>
           <span className="inline-flex items-center gap-1 bg-emerald-50 text-emerald-700 px-3 py-1 rounded-full text-xs font-bold uppercase">
             <Banknote size={14} /> ₹{taskMeta.budget}
           </span>
           <span className="inline-flex items-center gap-1 bg-blue-50 text-blue-700 px-3 py-1 rounded-full text-xs font-bold uppercase">
             <Timer size={14} /> {taskMeta.timeLimit} MIN
           </span>
        </div>
        
        <div className="p-4 bg-slate-50 border border-slate-100 rounded-2xl space-y-4 mt-6">
          {taskMeta.legs.map((leg: string, idx: number) => (
             <div key={idx} className="flex items-center gap-3 leg-step" style={{animationDelay: `${idx * 0.5}s`, opacity: 0}}>
                <div className="h-3 w-3 rounded-full bg-blue-500 animate-[pulse-glow_1.5s_infinite]" />
                <span className="text-sm font-semibold text-slate-700">Evaluating: {leg}</span>
             </div>
          ))}
        </div>
        
        <div className="relative h-1.5 w-full bg-slate-100 rounded-full overflow-hidden mt-8">
           <div className="absolute top-0 bottom-0 left-0 bg-gradient-to-r from-blue-500 to-purple-500 animate-[shimmer_2s_linear_infinite] w-1/2" style={{backgroundSize: '200% 100%'}} />
        </div>
        <p className="text-xs text-center text-slate-400 font-bold tracking-widest uppercase mt-2 animate-[blink_1s_infinite]">Evaluating all transport modes...</p>
      </div>
    </div>
  );

  const renderHighlightedPhase = () => (
    <div className="flex-1 p-6 flex flex-col items-center justify-center space-y-4">
       <Bot size={48} className="text-purple-600 animate-bounce" />
       <h2 className="text-xl font-bold font-['Space_Grotesk'] text-center">Route found!<br/>Highlighting optimal path...</h2>
    </div>
  );

  const renderDecidedPhase = () => (
    <div className="flex-1 overflow-y-auto bg-slate-50 custom-scrollbar pb-6 space-y-4">
      {/* Agent Decision Card */}
      <div className="m-4 rounded-2xl p-5 agent-decision-card">
        <div className="flex items-center gap-2 mb-4">
          <Bot size={20} className="text-purple-700" />
          <h3 className="text-sm font-black uppercase tracking-widest text-purple-700">Agent Decision</h3>
        </div>
        
        <h4 className="font-['Space_Grotesk'] font-bold text-lg mb-4">RECOMMENDED ROUTE</h4>
        
        <div className="space-y-3 mb-6 bg-white/60 p-4 rounded-xl border border-white/40">
           <div className="flex items-center gap-2">
             <span className="font-bold text-sm">✅ USE:</span>
             <span className="transport-pill-use">{usedMode}</span>
           </div>
           
           <div className="flex flex-wrap items-center gap-2">
             <span className="font-bold text-sm">❌ AVOID:</span>
             <div className="flex gap-2 flex-wrap">
               {doNotUseModes.map(m => (
                 <span key={m} className="transport-pill-nouse text-xs uppercase font-bold">{m}</span>
               ))}
             </div>
           </div>
        </div>
        
        <div className="grid grid-cols-2 gap-4 mb-4 text-sm font-bold bg-white/40 p-3 rounded-lg">
           <div>
             <span className="text-slate-500 block text-xs">Reward Score</span>
             <div className="flex items-center gap-2">
                <div className="h-1.5 flex-1 bg-slate-200 rounded-full overflow-hidden">
                  <div className="h-full bg-emerald-500" style={{width: `${(bestRoute?.reward_score || 0) * 100}%`}} />
                </div>
                <span>{(bestRoute?.reward_score || 0).toFixed(2)}</span>
             </div>
           </div>
           <div>
              <span className="text-slate-500 block text-xs">Time / Cost</span>
              <span className="text-slate-900">{bestRoute?.time} min / ₹{bestRoute?.cost}</span>
           </div>
           <div className="uppercase">
              <span className="text-slate-500 block text-xs">Weather</span>
              <span className="text-slate-900">{taskMeta.weather.replace('_', ' ')}</span>
           </div>
           <div>
              <span className="text-slate-500 block text-xs">Legs</span>
              <span className="text-slate-900">{taskMeta.legs.length} legs</span>
           </div>
        </div>

        <div className="mt-4">
          <span className="block text-xs font-bold text-slate-500 mb-1">Why this route?</span>
          <p className="text-sm font-medium text-slate-800 italic border-l-2 border-purple-400 pl-3">
             "{bestRoute?.description} Selected based on your ₹{taskMeta.budget} budget under {taskMeta.weather.replace('_', ' ')} conditions."
          </p>
        </div>
      </div>
      
      <div className="px-5 pt-2 pb-1 border-b border-slate-200">
         <h4 className="text-xs font-black uppercase tracking-widest text-slate-400">All Available Routes</h4>
      </div>

      <div className="divide-y divide-slate-100">
        {routes.map((route) => {
          const isBest = route.id === bestRouteId;
          const isSelected = route.id === selectedRouteId;
          
          return (
            <div key={route.id} className="relative">
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
    </div>
  );

  return (
    <aside className="relative flex h-full w-full flex-col bg-white overflow-hidden">
      {/* Header Tabs */}
      <div className="flex items-center justify-between px-4 pt-4 shrink-0">
        <div className="flex gap-4 border-b w-full pb-1">
          {modes.slice(0, 5).map((mode, i) => {
             const tabRoute = routes.find(r => r.transport_type === mode.type) || (mode.type === 'best' ? bestRoute : null);
             
             return (
              <button 
                key={i} 
                onClick={() => tabRoute && onSelectRoute(tabRoute.id)}
                className={`flex flex-col items-center pb-2 px-1 relative transition-colors ${i === 0 || (tabRoute && tabRoute.id === selectedRouteId) ? 'text-blue-600 after:absolute after:bottom-0 after:left-0 after:right-0 after:h-0.5 after:bg-blue-600' : 'text-slate-500 hover:text-slate-900'}`}
              >
                <div className="mb-1">{transportIcons[mode.type] || <Car size={34}/>}</div>
                <span className="text-[10px] font-medium">{mode.label}</span>
              </button>
             );
          })}
          <button className="flex items-center justify-center pb-2 text-slate-500">
            <X size={20} />
          </button>
        </div>
      </div>

      {agentPhase === 'analyzing' && renderAnalyzingPhase()}
      {agentPhase === 'highlighted' && renderHighlightedPhase()}
      {agentPhase === 'decided' && renderDecidedPhase()}
    </aside>
  );
};

export default Sidebar;
