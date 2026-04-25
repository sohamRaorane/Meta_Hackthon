import { useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import MapView from '../components/MapView';
import Sidebar from '../components/Sidebar';
import NavSidebar from '../components/NavSidebar';
import dummyRoutes from '../data/dummyRoutes';
import type { RouteInputState, RouteData } from '../types/route';

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
      // For demo purposes, if no input state, provide dummy
      const dummyInput: RouteInputState = {
        source: 'Andheri, Railway Colony',
        destination: 'Kurla, Station Brahmanwadi',
        budget: 500,
        time: 60
      };
      navigate('/map', { state: dummyInput, replace: true });
      return;
    }

    const timer = window.setTimeout(() => setPageLoading(false), 500);
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

  if (pageLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-white">
        <div className="flex flex-col items-center gap-4">
          <div className="h-12 w-12 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
          <p className="text-sm font-bold text-slate-900 tracking-tight">Initializing Mumbai Map...</p>
        </div>
      </div>
    );
  }

  if (!inputState) return null;

  return (
    <div className="relative flex h-screen w-screen bg-slate-50 selection:bg-blue-100 selection:text-blue-900 overflow-hidden">
      {/* 1. Main Navigation Icon Bar */}
      <NavSidebar />

      {/* 2. Directions Panel (Moves from Fixed to Flex for better layout) */}
      <div className="z-40 w-[400px] flex-shrink-0 border-r border-slate-200 bg-white shadow-xl shadow-slate-200/50">
        <Sidebar
          inputState={inputState}
          routes={dummyRoutes}
          selectedRouteId={selectedRouteId}
          bestRouteId={bestRoute?.id ?? ''}
          onSelectRoute={handleSelectRoute}
          onRecalculate={handleRecalculate}
        />
      </div>

      {/* 3. Main Map Content */}
      <main className="relative flex-1 h-full">
        <MapView
          routes={dummyRoutes}
          selectedRouteId={selectedRouteId}
          onSelectRoute={handleSelectRoute}
          source={sourceCoords}
          destination={destinationCoords}
        />
      </main>
    </div>
  );
};

export default MapPage;

