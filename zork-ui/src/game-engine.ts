import { spawn, type Subprocess } from "bun";
import type { GameEngineResponse } from "./types";

export class GameEngine {
  private process: Subprocess | null = null;
  private zorkFile: string;
  private buffer: string = "";
  private decoder: TextDecoder = new TextDecoder();
  private reader: ReadableStreamDefaultReader<Uint8Array> | null = null;

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

    // Create a persistent reader for the lifetime of the process
    // This avoids the ReadableStream lock issue
    if (this.process.stdout) {
      this.reader = this.process.stdout.getReader();
    }

    // Read initial output
    const response = await this.readJsonResponse();
    return response.output || "Game loaded.";
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
    if (!this.reader) {
      return {};
    }

    try {
      // Read chunks from the persistent reader until we have a complete JSON line
      while (true) {
        const { value, done } = await this.reader.read();

        if (done) {
          return { output: "", error: "Process ended" };
        }

        if (value) {
          this.buffer += this.decoder.decode(value, { stream: true });

          // Check if we have a complete JSON line
          const newlineIndex = this.buffer.indexOf("\n");
          if (newlineIndex >= 0) {
            const jsonLine = this.buffer.substring(0, newlineIndex);
            this.buffer = this.buffer.substring(newlineIndex + 1);

            try {
              const parsed = JSON.parse(jsonLine);
              return parsed;
            } catch (e) {
              console.error("Failed to parse JSON:", jsonLine);
              return { output: jsonLine };
            }
          }
        }
      }
    } catch (error) {
      console.error("Error reading from process:", error);
      throw error;
    }
  }

  async stop(): Promise<void> {
    // Release the reader before killing the process
    if (this.reader) {
      try {
        this.reader.releaseLock();
      } catch (e) {
        // Ignore errors when releasing
      }
      this.reader = null;
    }

    if (this.process) {
      this.process.kill();
      this.process = null;
    }
    this.buffer = "";
  }
}
