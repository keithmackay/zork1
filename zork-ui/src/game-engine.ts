import { spawn, type Subprocess } from "bun";
import type { GameEngineResponse } from "./types";

export class GameEngine {
  private process: Subprocess | null = null;
  private currentOutput: string = "";
  private buffer: string = "";

  async start(): Promise<string> {
    // Start Python ZIL interpreter with zork1.zil file
    this.process = spawn({
      cmd: ["python3", "-u", "-m", "zil_interpreter.cli.repl", "/Users/Keith.MacKay/Projects/zork1/zork1/zork1.zil"],
      stdout: "pipe",
      stdin: "pipe",
      stderr: "pipe",
      cwd: "/Users/Keith.MacKay/Projects/zork1",
    });

    // Read initial output (welcome message)
    await Bun.sleep(200); // Give the process time to start and load
    const output = await this.readOutput();
    return output;
  }

  async sendCommand(command: string): Promise<GameEngineResponse> {
    if (!this.process || !this.process.stdin) {
      throw new Error("Game engine not started");
    }

    // Send command
    this.process.stdin.write(`${command}\n`);

    // Wait for response
    await Bun.sleep(50);
    const output = await this.readOutput();

    // Check for death/completion
    const isDead = this.checkDeath(output);
    const isComplete = this.checkCompletion(output);

    return {
      output,
      isDead,
      isComplete,
    };
  }

  private async readOutput(): Promise<string> {
    if (!this.process || !this.process.stdout) {
      return "";
    }

    try {
      const reader = this.process.stdout.getReader();
      const chunks: Uint8Array[] = [];
      let totalBytes = 0;

      // Read available data with timeout
      const timeout = 200;
      const start = Date.now();

      while (Date.now() - start < timeout) {
        try {
          const { value, done } = await Promise.race([
            reader.read(),
            new Promise<{ value: undefined; done: boolean }>((resolve) =>
              setTimeout(() => resolve({ value: undefined, done: false }), 50)
            ),
          ]);

          if (done) break;
          if (value) {
            chunks.push(value);
            totalBytes += value.length;
          } else {
            // No data available
            if (chunks.length > 0) break;
            await Bun.sleep(10);
          }
        } catch (error) {
          break;
        }
      }

      reader.releaseLock();

      if (chunks.length > 0) {
        const combined = new Uint8Array(totalBytes);
        let offset = 0;
        for (const chunk of chunks) {
          combined.set(chunk, offset);
          offset += chunk.length;
        }
        return new TextDecoder().decode(combined);
      }

      return "";
    } catch (error) {
      return "";
    }
  }

  private checkDeath(output: string): boolean {
    const deathPhrases = [
      "you are dead",
      "you have died",
      "*** you have died ***",
      "game over",
    ];

    const lowerOutput = output.toLowerCase();
    return deathPhrases.some(phrase => lowerOutput.includes(phrase));
  }

  private checkCompletion(output: string): boolean {
    const completionPhrases = [
      "you have won",
      "congratulations",
      "you are victorious",
      "you have completed",
    ];

    const lowerOutput = output.toLowerCase();
    return completionPhrases.some(phrase => lowerOutput.includes(phrase));
  }

  async stop(): Promise<void> {
    if (this.process) {
      this.process.kill();
      this.process = null;
    }
  }
}
