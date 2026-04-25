import { useState } from 'react';
import { MapPin, Navigation, DollarSign, Clock, ArrowRight } from 'lucide-react';
import type { RouteInputState } from '../types/route';

interface InputFormProps {
  onSubmit: (values: RouteInputState) => void;
}

const InputForm: React.FC<InputFormProps> = ({ onSubmit }) => {
  const [source, setSource] = useState('');
  const [destination, setDestination] = useState('');
  const [budget, setBudget] = useState('');
  const [time, setTime] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError('');

    if (!source.trim() || !destination.trim()) {
      setError('Please enter both source and destination.');
      return;
    }

    const parsedBudget = Number(budget);
    const parsedTime = Number(time);

    if (!parsedBudget || parsedBudget <= 0) {
      setError('Please enter a valid budget.');
      return;
    }

    if (!parsedTime || parsedTime <= 0) {
      setError('Please enter a valid travel time.');
      return;
    }

    onSubmit({
      source: source.trim(),
      destination: destination.trim(),
      budget: parsedBudget,
      time: parsedTime,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-5">
        {/* Source Input */}
        <div className="relative group">
          <label className="mb-2 block text-[10px] font-bold uppercase tracking-widest text-slate-500 group-focus-within:text-blue-400 transition-colors">
            Starting Point
          </label>
          <div className="relative">
            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-blue-400 transition-colors">
              <MapPin size={18} />
            </div>
            <input
              value={source}
              onChange={(event) => setSource(event.target.value)}
              placeholder="e.g. Andheri, Mumbai"
              className="w-full rounded-2xl border border-white/5 bg-white/5 py-4 pl-12 pr-4 text-sm font-medium text-white placeholder:text-slate-600 transition-all focus:border-blue-500/50 focus:bg-white/10 focus:outline-none focus:ring-4 focus:ring-blue-500/10"
            />
          </div>
        </div>

        {/* Destination Input */}
        <div className="relative group">
          <label className="mb-2 block text-[10px] font-bold uppercase tracking-widest text-slate-500 group-focus-within:text-emerald-400 transition-colors">
            Where to?
          </label>
          <div className="relative">
            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-emerald-400 transition-colors">
               <Navigation size={18} className="rotate-45" />
            </div>
            <input
              value={destination}
              onChange={(event) => setDestination(event.target.value)}
              placeholder="e.g. Kurla Station"
              className="w-full rounded-2xl border border-white/5 bg-white/5 py-4 pl-12 pr-4 text-sm font-medium text-white placeholder:text-slate-600 transition-all focus:border-emerald-500/50 focus:bg-white/10 focus:outline-none focus:ring-4 focus:ring-emerald-500/10"
            />
          </div>
        </div>
      </div>

      <div className="grid gap-5 sm:grid-cols-2">
        {/* Budget Input */}
        <div className="relative group">
          <label className="mb-2 block text-[10px] font-bold uppercase tracking-widest text-slate-500 group-focus-within:text-blue-400 transition-colors">
            Budget (₹)
          </label>
          <div className="relative">
            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-blue-400 transition-colors">
              <DollarSign size={18} />
            </div>
            <input
              type="number"
              value={budget}
              onChange={(event) => setBudget(event.target.value)}
              placeholder="Max cost"
              className="w-full rounded-2xl border border-white/5 bg-white/5 py-4 pl-12 pr-4 text-sm font-medium text-white placeholder:text-slate-600 transition-all focus:border-blue-500/50 focus:bg-white/10 focus:outline-none focus:ring-4 focus:ring-blue-500/10"
            />
          </div>
        </div>

        {/* Time Input */}
        <div className="relative group">
          <label className="mb-2 block text-[10px] font-bold uppercase tracking-widest text-slate-500 group-focus-within:text-blue-400 transition-colors">
            Time (min)
          </label>
          <div className="relative">
            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-blue-400 transition-colors">
              <Clock size={18} />
            </div>
            <input
              type="number"
              value={time}
              onChange={(event) => setTime(event.target.value)}
              placeholder="Max duration"
              className="w-full rounded-2xl border border-white/5 bg-white/5 py-4 pl-12 pr-4 text-sm font-medium text-white placeholder:text-slate-600 transition-all focus:border-blue-500/50 focus:bg-white/10 focus:outline-none focus:ring-4 focus:ring-blue-500/10"
            />
          </div>
        </div>
      </div>

      {error && (
        <div className="rounded-xl bg-red-500/10 p-3 text-xs font-bold text-red-500 border border-red-500/20">
          {error}
        </div>
      )}

      <button
        type="submit"
        className="group relative flex w-full items-center justify-center gap-3 overflow-hidden rounded-2xl bg-gradient-to-r from-blue-600 to-indigo-600 py-5 text-sm font-black uppercase tracking-widest text-white transition-all hover:bg-blue-500 hover:shadow-[0_0_40px_rgba(37,99,235,0.4)] active:scale-[0.98] animate-[pulse-glow_3s_infinite]"
      >
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-[100%] group-hover:translate-x-[100%] transition-transform duration-1000" />
        <span>Run AI Agent</span>
        <ArrowRight size={18} className="transition-transform group-hover:translate-x-1" />
      </button>

      <div className="pt-4 text-center">
        <span className="inline-flex items-center gap-1.5 rounded-full border border-white/5 bg-white/[0.03] px-3 py-1 text-[10px] font-semibold text-slate-400">
          Powered by GRPO-Trained Qwen 2.5 · Meta Hackathon 2025
        </span>
      </div>
    </form>
  );
};

export default InputForm;


