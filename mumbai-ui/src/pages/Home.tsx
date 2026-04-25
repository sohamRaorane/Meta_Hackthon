import { useNavigate } from 'react-router-dom';
import InputForm from '../components/InputForm';
import type { RouteInputState } from '../types/route';

const Home: React.FC = () => {
  const navigate = useNavigate();

  const handleSubmit = (values: RouteInputState) => {
    navigate('/map', { state: values });
  };

  return (
    <main className="min-h-screen bg-slate-100 px-4 py-10 sm:px-6">
      <div className="relative mx-auto flex min-h-[calc(100vh-4rem)] w-full max-w-2xl items-center justify-center">
        <div className="pointer-events-none absolute inset-0 overflow-hidden">
          <div className="absolute left-[-14%] top-6 h-52 w-52 rounded-full bg-cyan-300/20 blur-3xl" />
          <div className="absolute right-[-10%] top-20 h-48 w-48 rounded-full bg-violet-400/15 blur-3xl" />
        </div>

        <div className="relative w-full rounded-[34px] border border-slate-200/60 bg-white/90 p-8 shadow-[0_30px_90px_rgba(15,23,42,0.12)] backdrop-blur-xl">
          <div className="space-y-3 text-center">
            <p className="text-xs uppercase tracking-[0.5em] text-slate-500">Mumbai Route Planner</p>
            <h1 className="text-3xl font-semibold tracking-tight text-slate-950 sm:text-4xl">
              Find the best route in minutes
            </h1>
            <p className="mx-auto max-w-xl text-sm leading-7 text-slate-600">
              Fill in your source, destination, budget and travel time to get the best Mumbai route suggestions.
            </p>
          </div>

          <div className="mt-8 rounded-[28px] border border-slate-200/70 bg-slate-950/5 p-6 shadow-[inset_0_0_0_1px_rgba(56,189,248,0.08),0_18px_40px_rgba(15,23,42,0.08)]">
            <div className="mb-5 rounded-full bg-gradient-to-r from-cyan-500 via-sky-500 to-indigo-500 px-3 py-2 text-xs font-semibold uppercase tracking-[0.35em] text-white shadow-[0_0_20px_rgba(56,189,248,0.22)]">
              Instant Route Planning
            </div>
            <InputForm onSubmit={handleSubmit} />
          </div>
        </div>
      </div>
    </main>
  );
};

export default Home;
