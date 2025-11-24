#!/usr/bin/env bun
/**
 * Test game selection functionality
 */

import { GameEngine } from "./src/game-engine";

async function testGameSelection() {
  console.log("🧪 Testing Game Selection\n");

  const gameFiles = [
    {
      name: "Test Game",
      file: "tests/fixtures/simple_game.zil",
    },
    // Zork I, II, III would be tested if files exist
    // { name: "Zork I", file: "zork1/zork1.zil" },
    // { name: "Zork II", file: "../zork2/zork2.zil" },
    // { name: "Zork III", file: "../zork3/zork3.zil" },
  ];

  for (const game of gameFiles) {
    console.log(`\n✓ Testing ${game.name}...`);

    try {
      const engine = new GameEngine(game.file);
      const welcomeMsg = await engine.start();
      console.log(`  Started successfully: "${welcomeMsg}"`);

      const response = await engine.sendCommand("look");
      console.log(`  Command response: "${response.output.substring(0, 50)}..."`);

      await engine.stop();
      console.log(`  ✅ ${game.name} works correctly`);
    } catch (error) {
      console.error(`  ❌ ${game.name} failed:`, error);
    }
  }

  console.log("\n✅ Game selection tests completed!");
}

testGameSelection();
