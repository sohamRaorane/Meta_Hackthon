export interface ModeInfo {
  mode: string;
  available: boolean;
  confidence: number;
  est_cost: number;
  est_time_min: number;
  est_time_max: number;
}

export interface Observation {
  episode_id?: string;
  echoed_message: string;
  current_location: string;
  destination: string;
  time_remaining_minutes: number;
  budget_remaining: number;
  weather: string;
  available_modes: ModeInfo[];
  known_disruptions: string[];
  mid_journey_update: string | null;
  timestep: number;
  reached?: boolean;
}

export interface ResetResponse {
  observation: Observation;
  reward: null;
  done: false;
}

export interface StepResponse {
  observation: Observation;
  reward: number;
  done: boolean;
}

export interface Task {
  name: string;
  origin: string;
  destination: string;
  legs: number;
  time_limit: number;
  budget: number;
  weather: string;
  max_steps: number;
  disruptions: string[];
}

export interface AgentAction {
  mode: string;
  reward: number;
  success: boolean;
}