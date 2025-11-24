import { spawn, type Subprocess } from "bun";
import type { GameEngineResponse } from "./types";

export class GameEngine {
  private process: Subprocess | null = null;
  private zorkFile: string;
  private buffer: string = "";

  constructor(zorkFile: string = "tests/fixtures/simple_game.zil") {
    this.zorkFile = zorkFile;
  }

  async start(): Promise<string> {
    // Start Python ZIL interpreter with JSON mode
    const projectRoot = "/Users/Keith.MacKay/Projects/zork1";
    const zorkPath = `${projectRoot}/${this.zorkFile}`;

    this.process = spawn({
      cmd: ["python3", "-m", "zil_interpreter", zorkPath, "--json"],
      stdout: "pipe",
      stdin: "pipe",
      stderr: "pipe",
      cwd: projectRoot,
    });

    // Read initial output
    const response = await this.readJsonResponse();
    return response.output || "";
  }

  async sendCommand(command: string): Promise<GameEngineResponse> {
    if (!this.process || !this.process.stdin) {
      throw new Error("Game engine not started");
    }

    // Send command using Bun's write method
    this.process.stdin.write(`${command}\n`);
    this.process.stdin.flush();

    // Read JSON response
    const response = await this.readJsonResponse();

    return {
      output: response.output || "",
      isDead: response.is_dead || false,
      isComplete: response.is_complete || false,
    };
  }

  private async readJsonResponse(): Promise<any> {
    if (!this.process || !this.process.stdout) {
      return {};
    }

    const stdout = this.process.stdout;
    const reader = stdout.getReader();

    try {
      while (true) {
        const { value, done } = await reader.read();

        if (done) {
          return { output: "", error: "Process ended" };
        }

        if (value) {
          this.buffer += new TextDecoder().decode(value);

          // Check if we have a complete JSON line
          const newlineIndex = this.buffer.indexOf("\n");
          if (newlineIndex >= 0) {
            const jsonLine = this.buffer.substring(0, newlineIndex);
            this.buffer = this.buffer.substring(newlineIndex + 1);

            try {
              const parsed = JSON.parse(jsonLine);
              reader.releaseLock();
              return parsed;
            } catch (e) {
              console.error("Failed to parse JSON:", jsonLine);
              reader.releaseLock();
              return { output: jsonLine };
            }
          }
        }
      }
    } catch (error) {
      reader.releaseLock();
      throw error;
    }
  }

  async stop(): Promise<void> {
    if (this.process) {
      this.process.kill();
      this.process = null;
    }
  }
}
