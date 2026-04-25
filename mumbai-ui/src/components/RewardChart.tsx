import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface RewardChartProps {
  rewards: number[];
}

const RewardChart: React.FC<RewardChartProps> = ({ rewards }) => {
  const data = rewards.map((reward, index) => ({
    step: index + 1,
    reward: reward,
  }));

  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-purple-500/20">
      <h2 className="text-2xl font-bold text-white mb-6">Reward History</h2>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis
              dataKey="step"
              stroke="#9CA3AF"
              label={{ value: 'Steps', position: 'insideBottom', offset: -5, style: { textAnchor: 'middle', fill: '#9CA3AF' } }}
            />
            <YAxis
              stroke="#9CA3AF"
              domain={[0, 1]}
              label={{ value: 'Reward', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle', fill: '#9CA3AF' } }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1F2937',
                border: '1px solid #4B5563',
                borderRadius: '8px',
                color: '#F9FAFB'
              }}
            />
            <Line
              type="monotone"
              dataKey="reward"
              stroke="#8B5CF6"
              strokeWidth={2}
              dot={{ fill: '#8B5CF6', strokeWidth: 2, r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default RewardChart;