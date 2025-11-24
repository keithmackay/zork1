#!/usr/bin/env bun
/**
 * Quick integration test for the Bun UI and Python JSON protocol
 */

import { GameEngine } from "./src/game-engine";

async function testIntegration() {
  console.log("🧪 Testing Zork Terminal UI Integration\n");

  const engine = new GameEngine("tests/fixtures/simple_game.zil");

  try {
    // Test 1: Start engine
    console.log("✓ Test 1: Starting game engine...");
    const welcomeMsg = await engine.start();
    console.log(`  Welcome message: "${welcomeMsg}"`);

    // Test 2: Send command
    console.log("\n✓ Test 2: Sending 'look' command...");
    const response1 = await engine.sendCommand("look");
    console.log(`  Output: "${response1.output}"`);
    console.log(`  Is Dead: ${response1.isDead}`);
    console.log(`  Is Complete: ${response1.isComplete}`);

    // Test 3: Send another command
    console.log("\n✓ Test 3: Sending 'inventory' command...");
    const response2 = await engine.sendCommand("inventory");
    console.log(`  Output: "${response2.output}"`);

    // Test 4: Invalid command
    console.log("\n✓ Test 4: Sending invalid command...");
    const response3 = await engine.sendCommand("xyzzy");
    console.log(`  Output: "${response3.output}"`);

    // Stop engine
    console.log("\n✓ Test 5: Stopping engine...");
    await engine.stop();

    console.log("\n✅ All integration tests passed!");
  } catch (error) {
    console.error("\n❌ Integration test failed:", error);
    await engine.stop();
    process.exit(1);
  }
}

testIntegration();
