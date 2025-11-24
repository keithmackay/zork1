export type GameVersion = "zork1" | "zork2" | "zork3";

export interface GameState {
  history: string[];
  lastCommand: string;
  timestamp: number;
  gameName: GameVersion;
  gameFile: string;
}

export interface SavedGame {
  name: string;
  timestamp: number;
  state: GameState;
}

export interface GameEngineResponse {
  output: string;
  isDead: boolean;
  isComplete: boolean;
  error?: string;
}
