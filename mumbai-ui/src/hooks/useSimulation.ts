import { useState, useCallback } from 'react';
import type { Observation, ResetResponse, StepResponse, Task, AgentAction } from '../types/env';
import { reset, step } from '../services/api';

export const useSimulation = () => {
  const [episodeId, setEpisodeId] = useState<string | null>(null);
  const [observation, setObservation] = useState<Observation | null>(null);
  const [rewards, setRewards] = useState<number[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [baselineActions, setBaselineActions] = useState<AgentAction[]>([]);
  const [trainedActions, setTrainedActions] = useState<AgentAction[]>([]);

  const handleReset = useCallback(async (task: Task) => {
    setIsLoading(true);
    setError(null);
    try {
      const response: ResetResponse = await reset(task.name);
      setEpisodeId(response.observation.episode_id || null);
      setObservation(response.observation);
      setRewards([]);
      setBaselineActions([]);
      setTrainedActions([]);
    } catch (err) {
      setError('Failed to reset simulation');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleStep = useCallback(async (action: string) => {
    if (!episodeId) return;
    setIsLoading(true);
    setError(null);
    try {
      const response: StepResponse = await step(episodeId, action);
      setObservation(response.observation);
      setRewards(prev => [...prev, response.reward]);

      // Simulate baseline agent (random choice)
      const availableModes = response.observation.available_modes.filter(m => m.available);
      const randomMode = availableModes[Math.floor(Math.random() * availableModes.length)];
      const baselineSuccess = randomMode ? Math.random() > 0.3 : false; // 70% success if available
      const baselineReward = baselineSuccess ? response.reward * 0.8 : response.reward * 0.2;
      setBaselineActions(prev => [...prev, {
        mode: randomMode?.mode || 'none',
        reward: baselineReward,
        success: baselineSuccess
      }]);

      // Trained agent (API response)
      const trainedSuccess = response.reward > 0.5; // Assume success if reward > 0.5
      setTrainedActions(prev => [...prev, {
        mode: action,
        reward: response.reward,
        success: trainedSuccess
      }]);

      if (response.done) {
        setEpisodeId(null);
      }
    } catch (err) {
      setError('Failed to perform step');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }, [episodeId]);

  return {
    episodeId,
    observation,
    rewards,
    isLoading,
    error,
    baselineActions,
    trainedActions,
    handleReset,
    handleStep,
  };
};