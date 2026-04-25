import { useNavigate } from 'react-router-dom';
import { Train, Bus, MapPin, Navigation as NavIcon } from 'lucide-react';
import InputForm from '../components/InputForm';
import type { RouteInputState } from '../types/route';

const Home: React.FC = () => {
  const navigate = useNavigate();

  const handleSubmit = (values: RouteInputState) => {
    navigate('/map', { state: values });
  };

  return (
    <main className="relative flex min-h-screen w-full flex-col items-center justify-center overflow-hidden bg-slate-950 px-4 py-20">
      {/* Background Decorative Elements */}
      <div className="absolute inset-0 z-0">
        <div className="absolute left-[-10%] top-[-10%] h-[500px] w-[500px] rounded-full bg-blue-600/20 blur-[120px]" />
        <div className="absolute right-[-5%] bottom-[-5%] h-[400px] w-[400px] rounded-full bg-emerald-500/10 blur-[100px]" />
        
        {/* Animated Transportation Lines */}
        <div className="absolute inset-0 opacity-20">
          <div className="absolute top-[20%] left-0 h-[100px] w-full border-t border-b border-blue-500/30 -rotate-3" />
          <div className="absolute top-[50%] left-0 h-[60px] w-full border-t border-b border-emerald-500/20 rotate-6" />
        </div>
      </div>

      <div className="relative z-10 w-full max-w-xl">
        {/* Main Content Card */}
        <div className="glass overflow-hidden rounded-[40px] border border-white/10 shadow-[0_32px_120px_rgba(0,0,0,0.5)]">
          {/* Header with Transport Icons */}
          <div className="bg-white/5 p-8 text-center border-b border-white/10">
            <div className="mb-6 flex items-center justify-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-600 text-white shadow-lg shadow-blue-500/30">
                <Train size={24} />
              </div>
              <div className="h-[2px] w-8 rounded-full bg-white/20" />
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-500 text-white shadow-lg shadow-emerald-500/30">
                <Bus size={24} />
              </div>
            </div>
            
            <span className="text-[10px] font-bold uppercase tracking-[0.6em] text-blue-400">
              Mumbai Connect
            </span>
            <h1 className="mt-3 text-4xl font-extrabold tracking-tight text-white sm:text-5xl">
              Route Planner
            </h1>
            <p className="mt-4 text-sm font-medium leading-relaxed text-slate-400">
              Optimize your daily commute through Mumbai's vast <br />
              network of trains, buses, and metro lines.
            </p>
          </div>

          {/* Form Section */}
          <div className="bg-slate-900/40 p-8 sm:p-10">
             <div className="mb-8 flex items-center gap-3">
               <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-500/20 text-blue-400">
                 <NavIcon size={16} />
               </div>
               <h2 className="text-lg font-bold text-white tracking-tight">Plan Your Journey</h2>
             </div>
             
             <InputForm onSubmit={handleSubmit} />
          </div>

          {/* Footer Info */}
          <div className="bg-white/[0.02] px-8 py-5 text-center">
            <p className="text-[10px] font-semibold uppercase tracking-widest text-slate-500">
              AI-Powered Route Optimization • Real-time Data
            </p>
          </div>
        </div>

        {/* Floating Background Illustration (Simplified) */}
        <div className="mt-12 flex justify-center gap-8 opacity-40">
           <Train className="text-white" size={32} />
           <Bus className="text-white" size={32} />
           <NavIcon className="text-white" size={32} />
        </div>
      </div>
    </main>
  );
};

export default Home;

