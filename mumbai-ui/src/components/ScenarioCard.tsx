import React from 'react';
import type { Task } from '../types/env';

interface ScenarioCardProps {
  task: Task;
  onSelect: (task: Task) => void;
}

const ScenarioCard: React.FC<ScenarioCardProps> = ({ task, onSelect }) => {
  return (
    <div
      className="bg-gray-800 rounded-lg p-6 cursor-pointer hover:bg-gray-700 transition-colors border border-purple-500/20 hover:border-purple-500/50"
      onClick={() => onSelect(task)}
    >
      <h3 className="text-xl font-bold text-white mb-2">{task.name.toUpperCase()}</h3>
      <p className="text-gray-300 mb-4">{task.origin} → {task.destination}</p>
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <span className="text-purple-400">Legs:</span> {task.legs}
        </div>
        <div>
          <span className="text-purple-400">Time:</span> {task.time_limit}min
        </div>
        <div>
          <span className="text-purple-400">Budget:</span> ₹{task.budget}
        </div>
        <div>
          <span className="text-purple-400">Weather:</span> {task.weather}
        </div>
      </div>
      <div className="mt-4">
        <span className={`px-2 py-1 rounded text-xs ${
          task.max_steps <= 3 ? 'bg-green-600' :
          task.max_steps <= 5 ? 'bg-yellow-600' :
          'bg-red-600'
        }`}>
          {task.max_steps <= 3 ? 'Easy' : task.max_steps <= 5 ? 'Medium' : 'Hard'}
        </span>
      </div>
    </div>
  );
};

export default ScenarioCard;