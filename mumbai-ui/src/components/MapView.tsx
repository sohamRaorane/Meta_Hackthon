import { useMemo, useState, useEffect } from 'react';
import { MapContainer, Marker, Polyline, Popup, TileLayer, Tooltip, ZoomControl } from 'react-leaflet';
import { Icon, DivIcon } from 'leaflet';
import { Search, Circle, Activity, Hotel, Layers, Maximize, Target, MoreVertical, Plus, Minus, CloudRain, Car, Clock } from 'lucide-react';
import type { RouteData } from '../types/route';

const markerIcon = new Icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

// Create a custom div icon for the moving vehicle
const createVehicleIcon = (type: string) => {
  const icons: Record<string, string> = {
    auto: '🛺',
    bus: '🚌',
    metro: '🚇',
    train: '🚆',
    walking: '🚶',
    cycling: '🚲',
  };
  
  return new DivIcon({
    html: `<div class="bg-white p-2 rounded-full shadow-2xl border-4 border-blue-600 flex items-center justify-center text-4xl animate-bounce transform scale-125">${icons[type] || '🚗'}</div>`,
    className: 'custom-div-icon',
    iconSize: [80, 80],
    iconAnchor: [40, 40],
  });
};

const routeColors: Record<string, string> = {
  metro: '#22c55e',
  bus: '#0ea5e9',
  auto: '#f59e0b',
  train: '#0f172a',
  walking: '#64748b',
  cycling: '#8b5cf6',
};

interface MapViewProps {
  routes: RouteData[];
  selectedRouteId: string;
  onSelectRoute: (id: string) => void;
  source: [number, number];
  destination: [number, number];
}

const MapView: React.FC<MapViewProps> = ({ routes, selectedRouteId, onSelectRoute, source, destination }) => {
  const [hoveredRouteId, setHoveredRouteId] = useState<string | null>(null);
  const [vehiclePosIndex, setVehiclePosIndex] = useState(0);

  const selectedRoute = useMemo(() => 
    routes.find(r => r.id === selectedRouteId), 
    [routes, selectedRouteId]
  );

  // Animation logic
  useEffect(() => {
    if (!selectedRoute) return;
    
    setVehiclePosIndex(0);
    const interval = setInterval(() => {
      setVehiclePosIndex(prev => {
        if (prev < selectedRoute.coordinates.length - 1) {
          return prev + 1;
        }
        return 0; // Loop animation
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [selectedRouteId, selectedRoute]);

  const center = useMemo(() => [19.09, 72.86] as [number, number], []);

  return (
    <div className="relative h-full w-full overflow-hidden bg-slate-100">
      {/* 1. Top-Left: Search & Filters */}
      <div className="absolute left-6 top-6 z-[1000] flex items-center gap-4">
        <div className="flex h-12 w-[340px] items-center gap-3 rounded-full border border-slate-200 bg-white shadow-[0_4px_20px_rgba(0,0,0,0.08)] px-4 backdrop-blur-xl">
          <Search size={18} className="text-slate-400" />
          <input 
            type="text" 
            placeholder="Search for landmarks..." 
            className="flex-1 bg-transparent text-sm font-medium outline-none placeholder:text-slate-400"
          />
          <div className="h-4 w-[1px] bg-slate-200" />
          <button className="text-slate-400 hover:text-slate-900">
             <MoreVertical size={18} />
          </button>
        </div>

        <div className="hidden xl:flex gap-2">
          {[
            { icon: <Circle size={14} />, label: 'Gas' },
            { icon: <Activity size={14} />, label: 'EV Station' },
            { icon: <Hotel size={14} />, label: 'Hotels' },
          ].map((chip, i) => (
            <button key={i} className="flex items-center gap-2 rounded-full border border-slate-200 bg-white/95 px-4 py-2.5 text-[11px] font-bold text-slate-700 shadow-md backdrop-blur-xl transition hover:bg-slate-50">
              {chip.icon}
              {chip.label}
            </button>
          ))}
        </div>
      </div>

      {/* 2. Top-Right: Weather/Traffic Overlay (Refined Size) */}
      <div className="absolute right-6 top-6 z-[1000] flex overflow-hidden rounded-[2rem] border border-slate-200/60 bg-white shadow-[0_20px_50px_rgba(0,0,0,0.1)] backdrop-blur-2xl">
         <div className="flex items-center gap-8 p-6">
            <div className="flex flex-col items-center gap-2 px-1">
               <CloudRain size={48} className="text-blue-500" strokeWidth={1.5} />
               <div className="text-center">
                  <div className="text-[10px] font-black uppercase tracking-widest text-slate-900">Heavy Rain</div>
                  <div className="text-[8px] font-bold text-slate-400">Environment</div>
               </div>
            </div>
            
            <div className="h-12 w-[1px] bg-slate-100" />
            
            <div className="flex flex-col items-center gap-2 px-1">
               <div className="flex -space-x-3">
                  <Car size={30} className="text-orange-400 opacity-40 translate-x-2" />
                  <Car size={40} className="text-orange-600 z-10" />
               </div>
               <div className="text-center">
                  <div className="text-[10px] font-black uppercase tracking-widest text-slate-900">High Traffic</div>
                  <div className="text-[8px] font-bold text-slate-400">Road Status</div>
               </div>
            </div>
            
            <div className="h-12 w-[1px] bg-slate-100" />
            
            <div className="flex flex-col items-center gap-2 px-1">
               <Clock size={48} className="text-slate-800" strokeWidth={1.2} />
               <div className="text-center">
                  <div className="text-[10px] font-black uppercase tracking-widest text-slate-900">Rush Hour</div>
                  <div className="text-[8px] font-bold text-slate-400">Local Time</div>
               </div>
            </div>
         </div>
      </div>

      {/* Map Content */}
      <MapContainer 
        center={center} 
        zoom={13} 
        scrollWheelZoom={true} 
        className="h-full w-full"
        zoomControl={false}
      >
        <TileLayer
          attribution='&copy; OpenStreetMap &copy; CartoDB'
          url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png"
        />
        
        <ZoomControl position="bottomright" />

        <Marker position={source} icon={markerIcon}>
          <Popup>Start Point</Popup>
        </Marker>
        <Marker position={destination} icon={markerIcon}>
          <Popup>Destination</Popup>
        </Marker>

        {/* Moving Vehicle Animation */}
        {selectedRoute && (
          <Marker 
            position={selectedRoute.coordinates[vehiclePosIndex] as [number, number]} 
            icon={createVehicleIcon(selectedRoute.transport_type)}
            zIndexOffset={1000}
          />
        )}

        {routes.map((route) => {
          const selected = route.id === selectedRouteId;
          const hovered = route.id === hoveredRouteId;
          const color = routeColors[route.transport_type] || '#475569';

          return (
            <Polyline
              key={route.id}
              positions={route.coordinates}
              pathOptions={{
                color: selected ? '#2563eb' : color,
                weight: selected ? 8 : 4,
                opacity: selected ? 1 : hovered ? 0.8 : 0.4,
                lineJoin: 'round',
                lineCap: 'round',
                dashArray: selected ? undefined : '10, 15',
              }}
              eventHandlers={{
                click: () => onSelectRoute(route.id),
                mouseover: () => setHoveredRouteId(route.id),
                mouseout: () => setHoveredRouteId(null),
              }}
            >
              <Tooltip direction="top" sticky opacity={1}>
                <div className="px-1 py-0.5">
                   <div className={`text-[10px] font-black uppercase tracking-tighter ${selected ? 'text-blue-600' : 'text-slate-500'}`}>
                     {route.transport_type} {selected && '• Best Route'}
                   </div>
                   <div className="text-xs font-bold text-slate-800">{route.time} min • ₹{route.cost}</div>
                </div>
              </Tooltip>
            </Polyline>
          );
        })}
      </MapContainer>

      {/* Map Action Controls */}
      <div className="absolute bottom-8 left-6 z-[1000] flex flex-col gap-3">
        <button className="flex h-11 items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 text-xs font-black uppercase tracking-wider text-slate-700 shadow-xl transition-all hover:bg-slate-50">
           <Layers size={16} />
           <span>Layers</span>
        </button>
      </div>

      <div className="absolute bottom-8 right-10 z-[1000] flex flex-col gap-3">
        <div className="flex flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-xl">
           <button className="p-3 hover:bg-slate-50 border-b border-slate-100 text-slate-600"><Plus size={20} /></button>
           <button className="p-3 hover:bg-slate-50 text-slate-600"><Minus size={20} /></button>
        </div>
        <button className="flex h-12 w-12 items-center justify-center rounded-xl border border-slate-200 bg-white text-blue-600 shadow-xl transition-all hover:bg-slate-50">
           <Target size={20} />
        </button>
      </div>
    </div>
  );
};
export default MapView;

