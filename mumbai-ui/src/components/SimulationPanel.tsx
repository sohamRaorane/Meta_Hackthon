import React from 'react';
import type { Observation } from '../types/env';

interface SimulationPanelProps {
  observation: Observation | null;
}

const SimulationPanel: React.FC<SimulationPanelProps> = ({ observation }) => {
  if (!observation) return null;

  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-purple-500/20">
      <h2 className="text-2xl font-bold text-white mb-6">Current State</h2>
      <div className="space-y-4">
        <div>
          <label className="text-purple-400 text-sm">Current Location</label>
          <p className="text-white text-lg">{observation.current_location}</p>
        </div>
        <div>
          <label className="text-purple-400 text-sm">Destination</label>
          <p className="text-white text-lg">{observation.destination}</p>
        </div>
        <div>
          <label className="text-purple-400 text-sm">Time Remaining</label>
          <p className="text-white text-lg">{observation.time_remaining_minutes} minutes</p>
        </div>
        <div>
          <label className="text-purple-400 text-sm">Budget Remaining</label>
          <p className="text-green-400 text-lg">₹{observation.budget_remaining}</p>
        </div>
        <div>
          <label className="text-purple-400 text-sm">Weather</label>
          <p className={`text-lg ${
            observation.weather === 'clear' ? 'text-blue-400' :
            observation.weather === 'light_rain' ? 'text-yellow-400' :
            'text-red-400'
          }`}>
            {observation.weather.replace('_', ' ')}
          </p>
        </div>
        <div>
          <label className="text-purple-400 text-sm">Available Modes</label>
          <div className="mt-2 space-y-1">
            {observation.available_modes.map((mode, index) => (
              <div key={index} className="flex justify-between text-sm">
                <span className="text-white">{mode.mode}</span>
                <span className="text-gray-400">₹{mode.est_cost} • {mode.est_time_min}-{mode.est_time_max}min</span>
              </div>
            ))}
          </div>
        </div>
        {observation.known_disruptions.length > 0 && (
          <div>
            <label className="text-purple-400 text-sm">Known Disruptions</label>
            <ul className="mt-2 space-y-1">
              {observation.known_disruptions.map((disruption, index) => (
                <li key={index} className="text-red-400 text-sm">• {disruption}</li>
              ))}
            </ul>
          </div>
        )}
        {observation.mid_journey_update && (
          <div>
            <label className="text-purple-400 text-sm">Mid-Journey Update</label>
            <p className="text-yellow-400 text-sm mt-1">{observation.mid_journey_update}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SimulationPanel;