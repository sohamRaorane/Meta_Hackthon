export type TransportType = 'metro' | 'bus' | 'auto' | 'train';

export interface RouteData {
  id: string;
  transport_type: TransportType;
  coordinates: [number, number][];
  time: number;
  cost: number;
  reward_score: number;
  description?: string;
}

export interface RouteInputState {
  source: string;
  destination: string;
  budget: number;
  time: number;
}
