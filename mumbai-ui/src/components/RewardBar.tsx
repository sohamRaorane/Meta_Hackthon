import React from 'react';

interface RewardBarProps {
  reward: number;
}

const RewardBar: React.FC<RewardBarProps> = ({ reward }) => {
  const getColor = (value: number) => {
    if (value < 0.3) return 'bg-red-500';
    if (value < 0.6) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  return (
    <div className="w-full">
      <div className="flex justify-between text-sm text-gray-300 mb-1">
        <span>Reward</span>
        <span>{reward.toFixed(2)}</span>
      </div>
      <div className="w-full bg-gray-700 rounded-full h-4">
        <div
          className={`h-4 rounded-full transition-all duration-300 ${getColor(reward)}`}
          style={{ width: `${reward * 100}%` }}
        ></div>
      </div>
    </div>
  );
};

export default RewardBar;