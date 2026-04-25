import React from 'react';
import type { AgentAction } from '../types/env';

interface AgentComparisonProps {
  baselineActions: AgentAction[];
  trainedActions: AgentAction[];
}

const AgentComparison: React.FC<AgentComparisonProps> = ({ baselineActions, trainedActions }) => {
  const latestBaseline = baselineActions[baselineActions.length - 1];
  const latestTrained = trainedActions[trainedActions.length - 1];

  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-purple-500/20">
      <h2 className="text-2xl font-bold text-white mb-6">Agent Comparison</h2>
      <div className="grid grid-cols-2 gap-6">
        {/* Baseline Agent */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-300">Baseline Agent (Random)</h3>
          {latestBaseline ? (
            <div className="space-y-2">
              <div>
                <span className="text-purple-400 text-sm">Chosen Mode:</span>
                <p className="text-white">{latestBaseline.mode}</p>
              </div>
              <div>
                <span className="text-purple-400 text-sm">Reward:</span>
                <p className={`font-bold ${latestBaseline.reward > 0.5 ? 'text-green-400' : latestBaseline.reward > 0.2 ? 'text-yellow-400' : 'text-red-400'}`}>
                  {latestBaseline.reward.toFixed(2)}
                </p>
              </div>
              <div>
                <span className="text-purple-400 text-sm">Status:</span>
                <span className={`px-2 py-1 rounded text-xs ${latestBaseline.success ? 'bg-green-600' : 'bg-red-600'}`}>
                  {latestBaseline.success ? 'Success' : 'Failure'}
                </span>
              </div>
            </div>
          ) : (
            <p className="text-gray-500">No actions yet</p>
          )}
        </div>

        {/* Trained Agent */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-300">Trained Agent (AI)</h3>
          {latestTrained ? (
            <div className="space-y-2">
              <div>
                <span className="text-purple-400 text-sm">Chosen Mode:</span>
                <p className="text-white">{latestTrained.mode}</p>
              </div>
              <div>
                <span className="text-purple-400 text-sm">Reward:</span>
                <p className={`font-bold ${latestTrained.reward > 0.5 ? 'text-green-400' : latestTrained.reward > 0.2 ? 'text-yellow-400' : 'text-red-400'}`}>
                  {latestTrained.reward.toFixed(2)}
                </p>
              </div>
              <div>
                <span className="text-purple-400 text-sm">Status:</span>
                <span className={`px-2 py-1 rounded text-xs ${latestTrained.success ? 'bg-green-600' : 'bg-red-600'}`}>
                  {latestTrained.success ? 'Success' : 'Failure'}
                </span>
              </div>
            </div>
          ) : (
            <p className="text-gray-500">No actions yet</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default AgentComparison;