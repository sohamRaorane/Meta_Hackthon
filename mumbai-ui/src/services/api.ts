import axios from 'axios';
import type { ResetResponse, StepResponse, Task, Observation } from '../types/env';

const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:7860';
const api = axios.create({
  baseURL,
});

const DUMMY_TASKS: Task[] = [
  {
    name: 'easy',
    origin: 'Andheri East',
    destination: 'Kurla',
    legs: 2,
    time_limit: 60,
    budget: 120,
    weather: 'clear',
    max_steps: 2,
    disruptions: [],
  },
  {
    name: 'medium',
    origin: 'Borivali',
    destination: 'CST',
    legs: 3,
    time_limit: 90,
    budget: 80,
    weather: 'heavy_rain',
    max_steps: 3,
    disruptions: ['Western line failure'],
  },
  {
    name: 'hard',
    origin: 'Churchgate',
    destination: 'BKC',
    legs: 4,
    time_limit: 85,
    budget: 75,
    weather: 'heavy_rain',
    max_steps: 4,
    disruptions: ['Train signal outage', 'Auto scarcity'],
  },
  {
    name: 'bonus',
    origin: 'Bandra',
    destination: 'Juhu',
    legs: 2,
    time_limit: 40,
    budget: 30,
    weather: 'light_rain',
    max_steps: 2,
    disruptions: ['Budget crisis'],
  },
];

interface DummyEpisode {
  task: Task;
  step: number;
  timeRemaining: number;
  budgetRemaining: number;
  done: boolean;
}

const DUMMY_EPISODES = new Map<string, DummyEpisode>();

const getDummyModes = (weather: string) => [
  { mode: 'metro', available: weather !== 'heavy_rain', confidence: 0.9, est_cost: 20, est_time_min: 12, est_time_max: 18 },
  { mode: 'train', available: weather !== 'heavy_rain', confidence: 0.8, est_cost: 15, est_time_min: 10, est_time_max: 16 },
  { mode: 'auto', available: weather !== 'heavy_rain', confidence: 0.65, est_cost: 30, est_time_min: 15, est_time_max: 25 },
  { mode: 'bus', available: true, confidence: 0.7, est_cost: 10, est_time_min: 18, est_time_max: 30 },
  { mode: 'walk', available: true, confidence: 0.95, est_cost: 0, est_time_min: 20, est_time_max: 35 },
];

const getCurrentLocation = (task: Task, step: number) => {
  if (step === 0) return task.origin;
  if (step === task.max_steps) return task.destination;
  return `${task.origin} midpoint`;
};

const buildDummyObservation = (episodeId: string, task: Task, step: number, timeRemaining: number, budgetRemaining: number, done: boolean): Observation => ({
  episode_id: episodeId,
  echoed_message: `Step ${step + 1} for ${task.origin} → ${task.destination}`,
  current_location: getCurrentLocation(task, step),
  destination: task.destination,
  time_remaining_minutes: timeRemaining,
  budget_remaining: budgetRemaining,
  weather: task.weather,
  available_modes: getDummyModes(task.weather),
  known_disruptions: task.disruptions,
  mid_journey_update: step === 1 ? 'Traffic and signal delays ahead.' : null,
  timestep: step,
  reached: done,
});

const createDummyReset = (task_name: string): ResetResponse => {
  const task = DUMMY_TASKS.find((item) => item.name === task_name) ?? DUMMY_TASKS[0];
  const episodeId = `dummy-${task.name}-${Date.now()}`;
  const episode: DummyEpisode = {
    task,
    step: 0,
    timeRemaining: task.time_limit,
    budgetRemaining: task.budget,
    done: false,
  };
  DUMMY_EPISODES.set(episodeId, episode);
  return {
    observation: buildDummyObservation(episodeId, task, 0, episode.timeRemaining, episode.budgetRemaining, false),
    reward: null,
    done: false,
  };
};

const createDummyStep = (episode_id: string, action: string): StepResponse => {
  const episode = DUMMY_EPISODES.get(episode_id);
  if (!episode) {
    throw new Error('No dummy session found for this episode. Please reset first.');
  }

  if (episode.done) {
    return {
      observation: buildDummyObservation(episode_id, episode.task, episode.step, episode.timeRemaining, episode.budgetRemaining, true),
      reward: 0,
      done: true,
    };
  }

  const availableModes = getDummyModes(episode.task.weather);
  const chosenMode = availableModes.find((m) => action.toLowerCase().includes(m.mode)) ?? availableModes[0];
  const success = chosenMode.available;
  const reward = success ? Number((0.4 + Math.random() * 0.5).toFixed(2)) : Number((0.1 + Math.random() * 0.2).toFixed(2));

  episode.step += 1;
  episode.timeRemaining = Math.max(0, episode.timeRemaining - chosenMode.est_time_min);
  episode.budgetRemaining = Math.max(0, episode.budgetRemaining - chosenMode.est_cost);

  episode.done = episode.step >= episode.task.max_steps || episode.timeRemaining <= 0 || episode.budgetRemaining <= 0;

  const observation = buildDummyObservation(
    episode_id,
    episode.task,
    episode.step,
    episode.timeRemaining,
    episode.budgetRemaining,
    episode.done,
  );

  if (episode.done) {
    DUMMY_EPISODES.delete(episode_id);
  }

  return {
    observation,
    reward,
    done: episode.done,
  };
};

export const reset = async (task_name: string): Promise<ResetResponse> => {
  try {
    const response = await api.post('/reset', { task_name });
    return response.data;
  } catch (err) {
    console.warn('Backend unavailable, using dummy reset data.', err);
    return createDummyReset(task_name);
  }
};

export const step = async (episode_id: string, action: string): Promise<StepResponse> => {
  try {
    const response = await api.post('/step', { episode_id, action: { message: action } });
    return response.data;
  } catch (err) {
    console.warn('Backend unavailable, using dummy step data.', err);
    return createDummyStep(episode_id, action);
  }
};

export const getTasks = async (): Promise<Task[]> => {
  try {
    const response = await api.get('/tasks');
    const data = response.data;

    if (Array.isArray(data)) {
      return data;
    }

    return Object.entries(data ?? {}).map(([name, task]) => ({
      name,
      ...(task as Omit<Task, 'name'>),
    }));
  } catch (err) {
    console.warn('Backend unavailable, using dummy tasks.', err);
    return DUMMY_TASKS;
  }
};