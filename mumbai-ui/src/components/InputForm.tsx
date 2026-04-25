import { useState } from 'react';
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
      setError('Please enter a valid budget greater than zero.');
      return;
    }

    if (!parsedTime || parsedTime <= 0) {
      setError('Please enter a valid travel time greater than zero.');
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
    <form onSubmit={handleSubmit} className="space-y-5">
      <div>
        <label className="block text-sm font-medium text-slate-700">Source location</label>
        <input
          value={source}
          onChange={(event) => setSource(event.target.value)}
          placeholder="e.g. Andheri East"
          className="mt-2 w-full rounded-[28px] border border-slate-200 bg-slate-950/5 px-4 py-3 text-slate-950 shadow-sm shadow-cyan-200/10 transition focus:border-cyan-400 focus:outline-none focus:ring-2 focus:ring-cyan-200/70"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-slate-700">Destination location</label>
        <input
          value={destination}
          onChange={(event) => setDestination(event.target.value)}
          placeholder="e.g. Kurla"
          className="mt-2 w-full rounded-[28px] border border-slate-200 bg-slate-950/5 px-4 py-3 text-slate-950 shadow-sm shadow-cyan-200/10 transition focus:border-cyan-400 focus:outline-none focus:ring-2 focus:ring-cyan-200/70"
        />
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label className="block text-sm font-medium text-slate-700">Budget (INR)</label>
          <input
            type="number"
            value={budget}
            onChange={(event) => setBudget(event.target.value)}
            placeholder="e.g. 100"
            className="mt-2 w-full rounded-[28px] border border-slate-200 bg-slate-950/5 px-4 py-3 text-slate-950 shadow-sm shadow-cyan-200/10 transition focus:border-cyan-400 focus:outline-none focus:ring-2 focus:ring-cyan-200/70"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700">Max travel time (min)</label>
          <input
            type="number"
            value={time}
            onChange={(event) => setTime(event.target.value)}
            placeholder="e.g. 45"
            className="mt-2 w-full rounded-[28px] border border-slate-200 bg-slate-950/5 px-4 py-3 text-slate-950 shadow-sm shadow-cyan-200/10 transition focus:border-cyan-400 focus:outline-none focus:ring-2 focus:ring-cyan-200/70"
          />
        </div>
      </div>
      {error && <p className="text-sm text-red-600">{error}</p>}
      <button
        type="submit"
        className="w-full rounded-full bg-gradient-to-r from-cyan-500 via-sky-500 to-indigo-500 px-6 py-3 text-white shadow-[0_12px_30px_rgba(56,189,248,0.35)] transition duration-300 hover:shadow-[0_18px_48px_rgba(56,189,248,0.45)]"
      >
        Find Routes
      </button>
    </form>
  );
};

export default InputForm;
