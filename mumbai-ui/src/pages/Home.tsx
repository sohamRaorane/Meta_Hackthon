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
    <main className="relative flex min-h-screen w-full flex-col items-center justify-center overflow-hidden bg-[var(--bg-home)] px-4 py-20 font-['DM_Sans']">
      {/* Background Decorative Elements */}
      <div className="absolute inset-0 z-0">
        <div className="absolute left-[10%] top-[20%] h-3 w-3 rounded-full bg-blue-500 shadow-[0_0_15px_#2563eb] animate-pulse" />
        <div className="absolute right-[20%] top-[30%] h-4 w-4 rounded-full bg-amber-500 shadow-[0_0_20px_#f59e0b] animate-pulse" style={{ animationDelay: '1s' }} />
        
        {/* Animated Transportation Lines */}
        <div className="absolute inset-x-0 bottom-0 h-[200px] bg-gradient-to-t from-blue-900/20 to-transparent" />
        
        {/* SVG Silhouette */}
        <svg className="absolute bottom-0 left-0 w-full h-auto opacity-30" viewBox="0 0 1440 320" preserveAspectRatio="none">
          <path fill="#ffffff" fillOpacity="0.05" d="M0,160L48,149.3C96,139,192,117,288,128C384,139,480,181,576,192C672,203,768,181,864,154.7C960,128,1056,96,1152,90.7C1248,85,1344,107,1392,117.3L1440,128L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path>
        </svg>

        {/* Floating particles */}
        {['🚇', '🚌', '🛺', '🚆', '🚶'].map((emoji, index) => (
          <div 
            key={index} 
            className="absolute text-3xl opacity-0"
            style={{ 
               left: `${20 + index * 15}%`, 
               bottom: '-20px',
               animation: 'float-up 8s linear infinite',
               animationDelay: `${index * 1.5}s`
            }}
          >
            {emoji}
          </div>
        ))}
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
            <h1 className="mt-3 text-4xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-300 to-emerald-400 sm:text-5xl font-['Space_Grotesk'] animate-[shimmer_3s_linear_infinite]" style={{backgroundSize: '200% auto'}}>
              Mumbai AI Navigator
            </h1>
            <p className="mt-4 text-sm font-medium leading-relaxed text-slate-400 font-['DM_Sans']">
              Your AI agent finds the smartest multi-leg route through Mumbai's chaos
            </p>
          </div>

          {/* Form Section */}
          <div className="bg-slate-900/40 p-8 sm:p-10">
             <div className="mb-8 flex items-center gap-3">
               <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-500/20 text-blue-400">
                 <NavIcon size={16} />
               </div>
               <h2 className="text-lg font-bold text-white tracking-tight font-['Space_Grotesk']">Plan Your Journey</h2>
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
      </div>
    </main>
  );
};

export default Home;

