import type { GameState } from "./types";
import * as readline from "readline";

export class TerminalUI {
  private readonly COLORS = {
    reset: "\x1b[0m",
    bright: "\x1b[1m",
    dim: "\x1b[2m",
    cyan: "\x1b[36m",
    green: "\x1b[32m",
    yellow: "\x1b[33m",
    red: "\x1b[31m",
    blue: "\x1b[34m",
    magenta: "\x1b[35m",
  };

  private rl: readline.Interface;

  constructor() {
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
      terminal: true,
    });
  }

  clear(): void {
    console.clear();
  }

  printBanner(): void {
    console.log(this.COLORS.cyan + this.COLORS.bright);
    console.log("╔════════════════════════════════════════════╗");
    console.log("║        ZORK Terminal Interpreter          ║");
    console.log("║   The Great Underground Empire (1980)     ║");
    console.log("╚════════════════════════════════════════════╝");
    console.log(this.COLORS.reset);
  }

  printOutput(text: string): void {
    if (text && text.trim()) {
      console.log(this.COLORS.green + text + this.COLORS.reset);
    }
  }

  printError(text: string): void {
    console.log(this.COLORS.red + "Error: " + text + this.COLORS.reset);
  }

  printInfo(text: string): void {
    console.log(this.COLORS.yellow + text + this.COLORS.reset);
  }

  printSuccess(text: string): void {
    console.log(this.COLORS.green + this.COLORS.bright + text + this.COLORS.reset);
  }

  async prompt(message: string = ""): Promise<string> {
    return new Promise((resolve) => {
      this.rl.question(this.COLORS.cyan + "> " + this.COLORS.reset, (answer) => {
        resolve(answer.trim());
      });
    });
  }

  async promptSaveName(): Promise<string> {
    console.log(this.COLORS.yellow + "\nEnter save name: " + this.COLORS.reset);
    return this.prompt();
  }

  printMenu(options: string[]): void {
    console.log(this.COLORS.bright + "\nOptions:" + this.COLORS.reset);
    options.forEach((option, index) => {
      console.log(`  ${this.COLORS.cyan}${index + 1}.${this.COLORS.reset} ${option}`);
    });
  }

  printSeparator(): void {
    console.log(this.COLORS.dim + "─".repeat(50) + this.COLORS.reset);
  }

  async confirm(message: string): Promise<boolean> {
    console.log(this.COLORS.yellow + message + " (y/n): " + this.COLORS.reset);
    const response = await this.prompt();
    return response.toLowerCase() === "y" || response.toLowerCase() === "yes";
  }

  close(): void {
    this.rl.close();
  }
}
