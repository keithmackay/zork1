import { spawn, type Subprocess } from "bun";
import type { GameEngineResponse } from "./types";

export class GameEngine {
  private process: Subprocess | null = null;
  private zorkFile: string;

  constructor(zorkFile: string = "zork1/zork1.zil") {
    this.zorkFile = zorkFile;
  }

  async start(): Promise<string> {
    // Start Python ZIL interpreter with JSON mode
    const zorkPath = `/Users/Keith.MacKay/Projects/zork1/${this.zorkFile}`;

    this.process = spawn({
      cmd: ["python3", "-m", "zil_interpreter", zorkPath, "--json"],
      stdout: "pipe",
      stdin: "pipe",
      stderr: "pipe",
      cwd: "/Users/Keith.MacKay/Projects/zork1",
    });

    // Read initial output
    const response = await this.readJsonResponse();
    return response.output || "";
  }

  async sendCommand(command: string): Promise<GameEngineResponse> {
    if (!this.process || !this.process.stdin) {
      throw new Error("Game engine not started");
    }

    // Send command
    const writer = this.process.stdin.getWriter();
    await writer.write(new TextEncoder().encode(`${command}\n`));
    writer.releaseLock();

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

    const reader = this.process.stdout.getReader();
    let buffer = "";

    try {
      while (true) {
        const { value, done } = await reader.read();

        if (done) break;

        if (value) {
          buffer += new TextDecoder().decode(value);

          // Check if we have a complete JSON line
          const newlineIndex = buffer.indexOf("\n");
          if (newlineIndex >= 0) {
            const jsonLine = buffer.substring(0, newlineIndex);
            buffer = buffer.substring(newlineIndex + 1);

            try {
              return JSON.parse(jsonLine);
            } catch (e) {
              console.error("Failed to parse JSON:", jsonLine);
              return { output: jsonLine };
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }

    return {};
  }

  async stop(): Promise<void> {
    if (this.process) {
      this.process.kill();
      this.process = null;
    }
  }
}
