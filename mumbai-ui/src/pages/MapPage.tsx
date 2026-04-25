import { useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import MapView from '../components/MapView';
import Sidebar from '../components/Sidebar';
import dummyRoutes from '../data/dummyRoutes';
import type { RouteInputState } from '../types/route';
import type { RouteData } from '../types/route';

const getLocationCoordinates = (label: string, isSource: boolean): [number, number] => {
  const normalized = label.toLowerCase();
  if (normalized.includes('andheri')) return [19.1194, 72.8468];
  if (normalized.includes('kurla')) return [19.0711, 72.8795];
  if (normalized.includes('bandra')) return [19.0544, 72.8407];
  if (normalized.includes('cst') || normalized.includes('chhatrapati')) return [18.9402, 72.8352];
  if (normalized.includes('churchgate')) return [18.9300, 72.8300];
  if (normalized.includes('juhu')) return [19.1039, 72.8265];
  return isSource ? [19.076, 72.8777] : [19.083, 72.892];
};

const selectBestRoute = (routes: RouteData[], budget: number, time: number): RouteData | null => {
  const validRoutes = routes.filter((route) => route.cost <= budget && route.time <= time);
  const candidates = validRoutes.length ? validRoutes : routes;
  return (
    [...candidates].sort((a, b) => {
      if (b.reward_score !== a.reward_score) return b.reward_score - a.reward_score;
      return a.time - b.time;
    })[0] ?? null
  );
};

const MapPage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const inputState = location.state as RouteInputState | null;
  const [selectedRouteId, setSelectedRouteId] = useState<string>('');
  const [pageLoading, setPageLoading] = useState(true);

  useEffect(() => {
    if (!inputState) {
      navigate('/', { replace: true });
      return;
    }

    const timer = window.setTimeout(() => setPageLoading(false), 300);
    return () => window.clearTimeout(timer);
  }, [inputState, navigate]);

  const bestRoute = useMemo(() => {
    if (!inputState) return null;
    return selectBestRoute(dummyRoutes, inputState.budget, inputState.time);
  }, [inputState]);

  useEffect(() => {
    if (bestRoute) {
      setSelectedRouteId(bestRoute.id);
    }
  }, [bestRoute]);

  const handleSelectRoute = (id: string) => {
    setSelectedRouteId(id);
  };

  const handleRecalculate = () => {
    if (bestRoute) setSelectedRouteId(bestRoute.id);
  };

  const sourceCoords = useMemo(
    () => getLocationCoordinates(inputState?.source ?? '', true),
    [inputState?.source],
  );

  const destinationCoords = useMemo(
    () => getLocationCoordinates(inputState?.destination ?? '', false),
    [inputState?.destination],
  );

  if (!inputState) return null;

  if (pageLoading) {
    return (
      <div className="min-h-screen bg-[#f8f9fa] flex items-center justify-center px-6">
        <div className="animate-fade-in rounded-[32px] border border-slate-200 bg-white/90 p-12 shadow-[0_24px_80px_rgba(15,23,42,0.08)]">
          <p className="text-xl font-semibold text-slate-900">Preparing your Mumbai routes...</p>
        </div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-slate-100 px-4 py-6 sm:px-8">
      <div className="mx-auto grid max-w-[1600px] gap-6 lg:grid-cols-[420px_1fr]">
        <Sidebar
          inputState={inputState}
          routes={dummyRoutes}
          selectedRouteId={selectedRouteId}
          bestRouteId={bestRoute?.id ?? ''}
          onSelectRoute={handleSelectRoute}
          onRecalculate={handleRecalculate}
        />
        <div className="flex min-h-[calc(100vh-3rem)] flex-col gap-4">
          <div className="rounded-[32px] border border-slate-200 bg-white/95 p-5 shadow-sm">
            <h1 className="text-3xl font-semibold text-slate-950">Explore routes on the map</h1>
            <p className="mt-2 text-sm text-slate-600">Best route is highlighted and optimized for your budget.</p>
          </div>
          <div className="relative h-[calc(100vh-7rem)] overflow-hidden rounded-[32px] border border-slate-200 bg-white shadow-sm">
            <div className="absolute left-5 top-5 z-20 flex flex-col gap-3 rounded-3xl border border-slate-200/70 bg-white/95 p-3 shadow-[0_20px_50px_rgba(15,23,42,0.12)] backdrop-blur-xl">
              <div className="flex items-center gap-3 rounded-3xl border border-slate-200/90 bg-slate-50 px-4 py-2 text-sm text-slate-600 shadow-sm">
                <span className="font-semibold text-slate-900">Search along the route</span>
              </div>
              <div className="flex flex-wrap gap-2">
                <button className="rounded-2xl border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-700 shadow-sm">Gas</button>
                <button className="rounded-2xl border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-700 shadow-sm">EV charging</button>
                <button className="rounded-2xl border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-700 shadow-sm">Hotels</button>
              </div>
            </div>
            <MapView
              routes={dummyRoutes}
              selectedRouteId={selectedRouteId}
              onSelectRoute={handleSelectRoute}
              source={sourceCoords}
              destination={destinationCoords}
            />
          </div>
        </div>
      </div>
    </main>
  );
};

export default MapPage;
