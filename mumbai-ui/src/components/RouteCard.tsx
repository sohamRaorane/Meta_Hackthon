import type { RouteData } from '../types/route';

const transportIcons: Record<string, string> = {
  metro: '🚇',
  bus: '🚌',
  auto: '🚖',
  train: '🚆',
};

interface RouteCardProps {
  route: RouteData;
  selected: boolean;
  best: boolean;
  onSelect: (id: string) => void;
}

const RouteCard: React.FC<RouteCardProps> = ({ route, selected, best, onSelect }) => {
  return (
    <button
      onClick={() => onSelect(route.id)}
      className={`w-full rounded-3xl border p-4 text-left transition shadow-sm ${
        selected ? 'border-slate-900 bg-slate-100 shadow-lg' : 'border-slate-200 bg-white hover:border-slate-400'
      }`}
    >
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <span className="text-2xl">{transportIcons[route.transport_type]}</span>
          <div>
            <p className="text-sm font-semibold text-slate-900 capitalize">{route.transport_type}</p>
            <p className="text-xs text-slate-500">{route.time} min · ₹{route.cost}</p>
          </div>
        </div>
        {best && (
          <span className="rounded-full bg-emerald-500 px-3 py-1 text-xs font-semibold text-white">Best Route</span>
        )}
      </div>
      {route.description && (
        <p className="mt-3 text-sm leading-6 text-slate-600">{route.description}</p>
      )}
      <div className="mt-4 flex items-center justify-between text-sm text-slate-600">
        <span className="font-medium text-slate-700">Confidence</span>
        <span className="font-semibold text-slate-900">{Math.round(route.reward_score * 100)}%</span>
      </div>
    </button>
  );
};

export default RouteCard;
