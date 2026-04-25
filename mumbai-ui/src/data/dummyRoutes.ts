import type { RouteData } from '../types/route';

const dummyRoutes: RouteData[] = [
  {
    id: 'route-auto-01',
    transport_type: 'auto',
    coordinates: [
      [19.1194, 72.8468], // Andheri E
      [19.1170, 72.8550], // Gundavali
      [19.1100, 72.8600], // WEH Junction
      [19.1000, 72.8650], // Marol Naka area
      [19.0900, 72.8720], // SCLR Start
      [19.0800, 72.8750], // Kalina Junction
      [19.0711, 72.8795], // Kurla Station
    ],
    time: 26,
    cost: 65,
    reward_score: 0.95,
    description: 'Fastest via SCLR and Western Express Highway.',
  },
  {
    id: 'route-bus-02',
    transport_type: 'bus',
    coordinates: [
      [19.1194, 72.8468], // Andheri E
      [19.1140, 72.8560],
      [19.1100, 72.8680], // JB Nagar
      [19.1080, 72.8800], // Marol
      [19.0950, 72.8850], // Sakinaka
      [19.0850, 72.8880], // Jarimari
      [19.0711, 72.8795], // Kurla Station
    ],
    time: 42,
    cost: 25,
    reward_score: 0.85,
    description: 'Direct BEST bus via Sakinaka and Kurla-Andheri Rd.',
  },
  {
    id: 'route-metro-03',
    transport_type: 'metro',
    coordinates: [
      [19.1194, 72.8468], // Andheri Metro
      [19.1160, 72.8580], // WEH Station
      [19.1120, 72.8670], // Chakala
      [19.1090, 72.8750], // Marol Naka
      [19.1060, 72.8830], // Sakinaka
      [19.1000, 72.8890], // Asalpha
      [19.0850, 72.8800], // Last leg by auto/walk
      [19.0711, 72.8795], // Kurla
    ],
    time: 32,
    cost: 45,
    reward_score: 0.88,
    description: 'Metro Line 1 up to Sakinaka, then quick transfer.',
  },
  {
    id: 'route-train-04',
    transport_type: 'train',
    coordinates: [
      [19.1194, 72.8468], // Andheri station
      [19.1050, 72.8350], // Vile Parle
      [19.0880, 72.8430], // Santacruz
      [19.0183, 72.8466], // Dadar (Interchange)
      [19.0400, 72.8600], // Matunga
      [19.0600, 72.8700], // Sion
      [19.0711, 72.8795], // Kurla
    ],
    time: 48,
    cost: 15,
    reward_score: 0.78,
    description: 'Western Line to Dadar, switch to Central Line.',
  },
  {
    id: 'route-walking-05',
    transport_type: 'walking',
    coordinates: [
      [19.1194, 72.8468],
      [19.1100, 72.8550],
      [19.1000, 72.8650],
      [19.0900, 72.8700],
      [19.0800, 72.8750],
      [19.0711, 72.8795],
    ],
    time: 145,
    cost: 0,
    reward_score: 0.4,
    description: 'Straight walk along the link road.',
  },
  {
    id: 'route-cycling-06',
    transport_type: 'cycling',
    coordinates: [
      [19.1194, 72.8468],
      [19.1150, 72.8580],
      [19.1050, 72.8650],
      [19.0950, 72.8750],
      [19.0711, 72.8795],
    ],
    time: 55,
    cost: 0,
    reward_score: 0.72,
    description: 'Scenic cycling route via JVLR shortcuts.',
  },
];

export default dummyRoutes;

