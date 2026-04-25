import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import type { Task } from '../types/env';
import { useSimulation } from '../hooks/useSimulation';
import SimulationPanel from '../components/SimulationPanel';
import AgentComparison from '../components/AgentComparison';
import RewardChart from '../components/RewardChart';

const Simulation: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const selectedTask: Task = location.state?.selectedTask;

  const {
    episodeId,
    observation,
    rewards,
    isLoading,
    error,
    baselineActions,
    trainedActions,
    handleReset,
    handleStep,
  } = useSimulation();

  const [action, setAction] = useState('');

  useEffect(() => {
    if (selectedTask && !episodeId) {
      handleReset(selectedTask);
    }
  }, [selectedTask, episodeId, handleReset]);

  const handleNextStep = () => {
    if (action.trim()) {
      handleStep(action);
      setAction('');
    }
  };

  if (!selectedTask) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-400 text-xl mb-4">No scenario selected</div>
          <button
            onClick={() => navigate('/scenario')}
            className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded"
          >
            Choose Scenario
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold text-white">Simulation: {selectedTask.name.toUpperCase()}</h1>
          <button
            onClick={() => navigate('/scenario')}
            className="bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded"
          >
            Change Scenario
          </button>
        </div>

        {error && (
          <div className="bg-red-900 border border-red-700 text-red-200 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          {/* Left Panel */}
          <div className="lg:col-span-1">
            <SimulationPanel observation={observation} />
          </div>

          {/* Right Panel */}
          <div className="lg:col-span-2">
            <AgentComparison baselineActions={baselineActions} trainedActions={trainedActions} />
          </div>
        </div>

        {/* Action Input */}
        {episodeId && observation && (
          <div className="bg-gray-800 rounded-lg p-6 border border-purple-500/20 mb-8">
            <h2 className="text-2xl font-bold text-white mb-4">Next Action</h2>
            <div className="flex gap-4">
              <input
                type="text"
                value={action}
                onChange={(e) => setAction(e.target.value)}
                placeholder="Describe your transport choice (e.g., 'Take metro')"
                className="flex-1 bg-gray-700 border border-gray-600 rounded px-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:border-purple-500"
                disabled={isLoading}
              />
              <button
                onClick={handleNextStep}
                disabled={isLoading || !action.trim()}
                className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-6 py-2 rounded font-semibold transition-colors"
              >
                {isLoading ? 'Processing...' : 'Next Step'}
              </button>
            </div>
            {observation.available_modes.length > 0 && (
              <div className="mt-4">
                <p className="text-gray-400 text-sm mb-2">Available modes:</p>
                <div className="flex flex-wrap gap-2">
                  {observation.available_modes.filter(m => m.available).map((mode) => (
                    <button
                      key={mode.mode}
                      onClick={() => setAction(`Take ${mode.mode}`)}
                      className="bg-gray-700 hover:bg-gray-600 text-white px-3 py-1 rounded text-sm transition-colors"
                    >
                      {mode.mode} (₹{mode.est_cost})
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Reward Chart */}
        <RewardChart rewards={rewards} />

        {!episodeId && observation && (
          <div className="text-center mt-8">
            <div className="text-green-400 text-xl mb-4">Simulation Complete!</div>
            <button
              onClick={() => navigate('/scenario')}
              className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded font-semibold"
            >
              Run Another Simulation
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Simulation;