import type { RouteData } from '../types/route';

const dummyRoutes: RouteData[] = [
  {
    id: 'route-auto-01',
    transport_type: 'auto',
    coordinates: [
      [19.1194, 72.8468],
      [19.1160, 72.8530],
      [19.1100, 72.8600],
      [19.0990, 72.8690],
      [19.0870, 72.8760],
      [19.0711, 72.8795],
    ],
    time: 26,
    cost: 65,
    reward_score: 0.88,
    description: 'Fastest by taxi across western and eastern corridors',
  },
  {
    id: 'route-bus-02',
    transport_type: 'bus',
    coordinates: [
      [19.1194, 72.8468],
      [19.1140, 72.8545],
      [19.1065, 72.8638],
      [19.0938, 72.8698],
      [19.0816, 72.8769],
      [19.0711, 72.8795],
    ],
    time: 36,
    cost: 35,
    reward_score: 0.81,
    description: 'Scheduled city bus route using major junctions',
  },
  {
    id: 'route-metro-03',
    transport_type: 'metro',
    coordinates: [
      [19.1194, 72.8468],
      [19.1189, 72.8269],
      [19.1110, 72.8357],
      [19.1080, 72.8578],
      [19.0950, 72.8710],
      [19.0711, 72.8795],
    ],
    time: 32,
    cost: 55,
    reward_score: 0.79,
    description: 'Metro to Marol Naka then last-mile auto to Kurla',
  },
  {
    id: 'route-train-04',
    transport_type: 'train',
    coordinates: [
      [19.1194, 72.8468],
      [19.0550, 72.8357],
      [19.0183, 72.8466],
      [19.0728, 72.8798],
    ],
    time: 42,
    cost: 30,
    reward_score: 0.72,
    description: 'Local suburban train via Dadar interchange',
  },
];

export default dummyRoutes;
