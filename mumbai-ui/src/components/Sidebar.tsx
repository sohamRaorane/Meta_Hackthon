import type { RouteData, RouteInputState } from '../types/route';
import RouteCard from './RouteCard';

interface SidebarProps {
  inputState: RouteInputState;
  routes: RouteData[];
  selectedRouteId: string;
  bestRouteId: string;
  onSelectRoute: (id: string) => void;
  onRecalculate: () => void;
}

const ROUTE_COLORS: Record<string, string> = {
  metro: 'bg-emerald-500',
  bus: 'bg-sky-500',
  auto: 'bg-amber-400',
  train: 'bg-slate-900',
};

const Sidebar: React.FC<SidebarProps> = ({
  inputState,
  routes,
  selectedRouteId,
  bestRouteId,
  onSelectRoute,
  onRecalculate,
}) => {
  return (
    <aside className="flex h-full flex-col rounded-[32px] border border-slate-200 bg-white p-5 shadow-[0_40px_100px_rgba(15,23,42,0.05)]">
      <div className="space-y-4 pb-4 border-b border-slate-200">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-slate-500">Route details</p>
          <h2 className="text-2xl font-semibold text-slate-950">Explore routes</h2>
        </div>

        <div className="space-y-3 rounded-[28px] border border-slate-200/80 bg-slate-50 p-4">
          <div className="rounded-3xl border border-slate-200 bg-white px-4 py-3 shadow-sm">
            <p className="text-[11px] uppercase tracking-[0.38em] text-slate-500">From</p>
            <p className="mt-2 text-sm font-semibold text-slate-900">{inputState.source}</p>
          </div>
          <div className="rounded-3xl border border-slate-200 bg-white px-4 py-3 shadow-sm">
            <p className="text-[11px] uppercase tracking-[0.38em] text-slate-500">To</p>
            <p className="mt-2 text-sm font-semibold text-slate-900">{inputState.destination}</p>
          </div>
        </div>

        <div className="grid gap-3 sm:grid-cols-2">
          <div className="rounded-[24px] border border-slate-200 bg-white p-3 shadow-sm">
            <p className="text-[11px] uppercase tracking-[0.3em] text-slate-500">Budget</p>
            <p className="mt-2 text-lg font-semibold text-slate-950">₹{inputState.budget}</p>
          </div>
          <div className="rounded-[24px] border border-slate-200 bg-white p-3 shadow-sm">
            <p className="text-[11px] uppercase tracking-[0.3em] text-slate-500">Max time</p>
            <p className="mt-2 text-lg font-semibold text-slate-950">{inputState.time} min</p>
          </div>
        </div>

        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="text-[11px] uppercase tracking-[0.3em] text-slate-500">Quick filters</p>
          </div>
          <button
            onClick={onRecalculate}
            className="rounded-full bg-slate-950 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800"
          >
            Recalculate
          </button>
        </div>

        <div className="grid gap-2 sm:grid-cols-2">
          {Object.entries(ROUTE_COLORS).map(([type, color]) => (
            <div key={type} className="flex items-center gap-3 rounded-3xl border border-slate-200 p-3">
              <span className={`inline-block h-3 w-3 rounded-full ${color}`} />
              <span className="text-sm text-slate-700 capitalize">{type}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-6 flex-1 overflow-y-auto space-y-4 pr-1 pb-4">
        {routes.map((route) => (
          <RouteCard
            key={route.id}
            route={route}
            selected={route.id === selectedRouteId}
            best={route.id === bestRouteId}
            onSelect={onSelectRoute}
          />
        ))}
      </div>
    </aside>
  );
};

export default Sidebar;
