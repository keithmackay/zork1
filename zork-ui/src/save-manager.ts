import { mkdir, readdir, readFile, writeFile, unlink } from "fs/promises";
import { join } from "path";
import type { GameState, SavedGame } from "./types";

export class SaveManager {
  private savesDir: string;

  constructor(savesDir: string = "/Users/Keith.MacKay/Projects/zork1/zork-ui/saves") {
    this.savesDir = savesDir;
  }

  async initialize(): Promise<void> {
    try {
      await mkdir(this.savesDir, { recursive: true });
    } catch (error) {
      // Directory might already exist
    }
  }

  async saveGame(name: string, state: GameState): Promise<void> {
    const savedGame: SavedGame = {
      name,
      timestamp: Date.now(),
      state,
    };

    const filename = this.sanitizeFilename(name);
    const filepath = join(this.savesDir, `${filename}.json`);

    await writeFile(filepath, JSON.stringify(savedGame, null, 2));
  }

  async loadGame(name: string): Promise<GameState | null> {
    try {
      const filename = this.sanitizeFilename(name);
      const filepath = join(this.savesDir, `${filename}.json`);

      const content = await readFile(filepath, "utf-8");
      const savedGame: SavedGame = JSON.parse(content);

      return savedGame.state;
    } catch (error) {
      return null;
    }
  }

  async listSaves(): Promise<SavedGame[]> {
    try {
      const files = await readdir(this.savesDir);
      const saves: SavedGame[] = [];

      for (const file of files) {
        if (file.endsWith(".json")) {
          try {
            const filepath = join(this.savesDir, file);
            const content = await readFile(filepath, "utf-8");
            const savedGame: SavedGame = JSON.parse(content);
            saves.push(savedGame);
          } catch (error) {
            // Skip invalid save files
          }
        }
      }

      return saves.sort((a, b) => b.timestamp - a.timestamp);
    } catch (error) {
      return [];
    }
  }

  async deleteSave(name: string): Promise<boolean> {
    try {
      const filename = this.sanitizeFilename(name);
      const filepath = join(this.savesDir, `${filename}.json`);
      await unlink(filepath);
      return true;
    } catch (error) {
      return false;
    }
  }

  private sanitizeFilename(name: string): string {
    return name
      .toLowerCase()
      .replace(/[^a-z0-9_-]/g, "_")
      .substring(0, 50);
  }
}
