import { useMemo, useState } from 'react';
import { MapContainer, Marker, Polyline, Popup, TileLayer, Tooltip } from 'react-leaflet';
import { Icon } from 'leaflet';
import type { RouteData } from '../types/route';

const markerIcon = new Icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const routeColors: Record<string, string> = {
  metro: '#22c55e',
  bus: '#0ea5e9',
  auto: '#f59e0b',
  train: '#0f172a',
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

  const center = useMemo(() => [19.076, 72.8777] as [number, number], []);

  return (
    <div className="h-full rounded-3xl border border-slate-200 bg-white shadow-sm">
      <MapContainer center={center} zoom={12} scrollWheelZoom={true} className="h-full rounded-3xl">
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors — CartoDB Voyager'
          url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png"
        />
        <Marker position={source} icon={markerIcon}>
          <Popup>Source</Popup>
        </Marker>
        <Marker position={destination} icon={markerIcon}>
          <Popup>Destination</Popup>
        </Marker>

        {routes.map((route) => {
          const selected = route.id === selectedRouteId;
          const hovered = route.id === hoveredRouteId;
          const color = routeColors[route.transport_type] || '#334155';

          return (
            <Polyline
              key={route.id}
              positions={route.coordinates}
              pathOptions={{
                color,
                weight: selected ? 8 : 5,
                opacity: hovered || selected ? 1 : 0.75,
                dashArray: selected ? undefined : '8',
              }}
              eventHandlers={{
                click: () => onSelectRoute(route.id),
                mouseover: () => setHoveredRouteId(route.id),
                mouseout: () => setHoveredRouteId(null),
              }}
              className={selected ? 'route-glow' : ''}
            >
              <Tooltip direction="top" sticky>
                <div className="text-sm font-semibold">{route.transport_type.toUpperCase()}</div>
                <div className="text-xs">{route.time} min • ₹{route.cost}</div>
              </Tooltip>
            </Polyline>
          );
        })}
      </MapContainer>
    </div>
  );
};

export default MapView;
