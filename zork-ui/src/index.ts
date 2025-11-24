import { GameEngine } from "./game-engine";
import { SaveManager } from "./save-manager";
import { TerminalUI } from "./ui";
import type { GameState } from "./types";

class ZorkTerminal {
  private engine: GameEngine;
  private saveManager: SaveManager;
  private ui: TerminalUI;
  private gameState: GameState;
  private isRunning: boolean = false;

  constructor() {
    this.engine = new GameEngine();
    this.saveManager = new SaveManager();
    this.ui = new TerminalUI();
    this.gameState = {
      history: [],
      lastCommand: "",
      timestamp: Date.now(),
      gameName: "zork1",
    };
  }

  async initialize(): Promise<void> {
    await this.saveManager.initialize();
    this.ui.clear();
    this.ui.printBanner();
  }

  async showMainMenu(): Promise<void> {
    this.ui.printSeparator();
    this.ui.printMenu([
      "Start New Game",
      "Load Saved Game",
      "List Saves",
      "Exit",
    ]);

    const choice = await this.ui.prompt("Choose option (1-4)");

    switch (choice) {
      case "1":
        await this.startNewGame();
        break;
      case "2":
        await this.loadGameMenu();
        break;
      case "3":
        await this.listSavesMenu();
        break;
      case "4":
        await this.exit();
        break;
      default:
        this.ui.printError("Invalid option");
        await this.showMainMenu();
    }
  }

  async startNewGame(): Promise<void> {
    this.ui.clear();
    this.ui.printInfo("Starting new game...");

    try {
      const welcomeMessage = await this.engine.start();
      this.isRunning = true;
      this.gameState = {
        history: [],
        lastCommand: "",
        timestamp: Date.now(),
        gameName: "zork1",
      };

      // Display welcome message
      this.ui.printOutput(welcomeMessage);

      await this.gameLoop();
    } catch (error) {
      this.ui.printError(`Failed to start game: ${error}`);
      await this.showMainMenu();
    }
  }

  async gameLoop(): Promise<void> {
    while (this.isRunning) {
      const command = await this.ui.prompt();

      if (!command) continue;

      // Handle special commands
      if (command.toLowerCase() === "save") {
        await this.handleSave();
        continue;
      }

      if (command.toLowerCase() === "load") {
        await this.handleLoad();
        continue;
      }

      if (command.toLowerCase() === "quit" || command.toLowerCase() === "exit") {
        const confirm = await this.ui.confirm("Are you sure you want to quit?");
        if (confirm) {
          await this.engine.stop();
          await this.showMainMenu();
          return;
        }
        continue;
      }

      // Send command to game engine
      try {
        const response = await this.engine.sendCommand(command);

        // Update game state
        this.gameState.history.push(command);
        this.gameState.lastCommand = command;

        // Display output
        this.ui.printOutput(response.output);

        // Check for death or completion
        if (response.isDead) {
          await this.handleDeath();
          return;
        }

        if (response.isComplete) {
          await this.handleCompletion();
          return;
        }
      } catch (error) {
        this.ui.printError(`Command failed: ${error}`);
      }
    }
  }

  async handleSave(): Promise<void> {
    const saveName = await this.ui.promptSaveName();

    if (!saveName) {
      this.ui.printError("Save cancelled");
      return;
    }

    try {
      await this.saveManager.saveGame(saveName, this.gameState);
      this.ui.printSuccess(`Game saved as "${saveName}"`);
    } catch (error) {
      this.ui.printError(`Failed to save game: ${error}`);
    }
  }

  async handleLoad(): Promise<void> {
    const saves = await this.saveManager.listSaves();

    if (saves.length === 0) {
      this.ui.printInfo("No saved games found");
      return;
    }

    this.ui.printInfo("\nSaved Games:");
    saves.forEach((save, index) => {
      const date = new Date(save.timestamp).toLocaleString();
      console.log(`  ${index + 1}. ${save.name} (${date})`);
    });

    const choice = await this.ui.prompt("Enter save number to load (or 0 to cancel)");
    const index = parseInt(choice) - 1;

    if (index < 0 || index >= saves.length) {
      this.ui.printInfo("Load cancelled");
      return;
    }

    const loadedState = await this.saveManager.loadGame(saves[index].name);

    if (loadedState) {
      this.gameState = loadedState;
      this.ui.printSuccess("Game loaded successfully!");

      // Restart engine with loaded state
      await this.engine.stop();
      const welcomeMessage = await this.engine.start();

      // Replay commands to restore state
      this.ui.printInfo("Restoring game state...");
      for (const cmd of loadedState.history) {
        await this.engine.sendCommand(cmd);
      }

      this.ui.printSuccess("State restored!");
    } else {
      this.ui.printError("Failed to load game");
    }
  }

  async loadGameMenu(): Promise<void> {
    const saves = await this.saveManager.listSaves();

    if (saves.length === 0) {
      this.ui.printInfo("No saved games found");
      await this.showMainMenu();
      return;
    }

    this.ui.printInfo("\nSaved Games:");
    saves.forEach((save, index) => {
      const date = new Date(save.timestamp).toLocaleString();
      console.log(`  ${index + 1}. ${save.name} (${date})`);
    });

    const choice = await this.ui.prompt("Enter save number to load (or 0 to cancel)");
    const index = parseInt(choice) - 1;

    if (index < 0 || index >= saves.length) {
      await this.showMainMenu();
      return;
    }

    const loadedState = await this.saveManager.loadGame(saves[index].name);

    if (loadedState) {
      this.gameState = loadedState;

      try {
        const welcomeMessage = await this.engine.start();
        this.isRunning = true;

        // Replay commands
        this.ui.printInfo("Restoring game state...");
        for (const cmd of loadedState.history) {
          await this.engine.sendCommand(cmd);
        }

        this.ui.printSuccess("Game loaded!");
        await this.gameLoop();
      } catch (error) {
        this.ui.printError(`Failed to load game: ${error}`);
        await this.showMainMenu();
      }
    } else {
      this.ui.printError("Failed to load game");
      await this.showMainMenu();
    }
  }

  async listSavesMenu(): Promise<void> {
    const saves = await this.saveManager.listSaves();

    if (saves.length === 0) {
      this.ui.printInfo("No saved games found");
    } else {
      this.ui.printInfo("\nSaved Games:");
      saves.forEach((save) => {
        const date = new Date(save.timestamp).toLocaleString();
        console.log(`  - ${save.name} (${date})`);
      });
    }

    await this.ui.prompt("Press Enter to continue");
    await this.showMainMenu();
  }

  async handleDeath(): Promise<void> {
    this.ui.printSeparator();
    this.ui.printError("YOU HAVE DIED!");
    this.ui.printSeparator();

    this.ui.printMenu([
      "Restart Game",
      "Load Saved Game",
      "Return to Main Menu",
    ]);

    const choice = await this.ui.prompt("Choose option (1-3)");

    await this.engine.stop();
    this.isRunning = false;

    switch (choice) {
      case "1":
        await this.startNewGame();
        break;
      case "2":
        await this.loadGameMenu();
        break;
      default:
        await this.showMainMenu();
    }
  }

  async handleCompletion(): Promise<void> {
    this.ui.printSeparator();
    this.ui.printSuccess("CONGRATULATIONS! YOU HAVE COMPLETED THE GAME!");
    this.ui.printSeparator();

    this.ui.printMenu([
      "Start New Game",
      "Load Different Save",
      "Return to Main Menu",
    ]);

    const choice = await this.ui.prompt("Choose option (1-3)");

    await this.engine.stop();
    this.isRunning = false;

    switch (choice) {
      case "1":
        await this.startNewGame();
        break;
      case "2":
        await this.loadGameMenu();
        break;
      default:
        await this.showMainMenu();
    }
  }

  async exit(): Promise<void> {
    this.ui.printInfo("Thank you for playing!");
    await this.engine.stop();
    this.ui.close();
    process.exit(0);
  }

  async run(): Promise<void> {
    await this.initialize();
    await this.showMainMenu();
  }
}

// Main entry point
const terminal = new ZorkTerminal();
terminal.run().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
