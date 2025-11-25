#!/usr/bin/env bun

/**
 * Test script to verify game-engine fixes:
 * 1. Initial prompt is shown (not empty)
 * 2. Multiple commands work without ReadableStream errors
 */

import { GameEngine } from "../src/game-engine";

async function runTests() {
  console.log("🧪 Testing Game Engine Fixes\n");

  const engine = new GameEngine("tests/fixtures/simple_game.zil");

  try {
    // Test 1: Initial prompt should be shown
    console.log("Test 1: Checking initial prompt...");
    const welcomeMessage = await engine.start();
    console.log(`  ✓ Received initial output: "${welcomeMessage.substring(0, 50)}..."`);

    if (!welcomeMessage || welcomeMessage.trim() === "") {
      console.error("  ✗ FAILED: Initial prompt is empty!");
      process.exit(1);
    }
    console.log("  ✓ PASSED: Initial prompt is not empty\n");

    // Test 2: First command should work
    console.log("Test 2: Sending first command (look)...");
    const response1 = await engine.sendCommand("look");
    console.log(`  ✓ Response: "${response1.output.substring(0, 50)}..."`);
    console.log("  ✓ PASSED: First command successful\n");

    // Test 3: Second command should work (this would fail with old code)
    console.log("Test 3: Sending second command (inventory)...");
    const response2 = await engine.sendCommand("inventory");
    console.log(`  ✓ Response: "${response2.output.substring(0, 50)}..."`);
    console.log("  ✓ PASSED: Second command successful\n");

    // Test 4: Third command to ensure stream is still working
    console.log("Test 4: Sending third command (look)...");
    const response3 = await engine.sendCommand("look");
    console.log(`  ✓ Response: "${response3.output.substring(0, 50)}..."`);
    console.log("  ✓ PASSED: Third command successful\n");

    // Clean up
    await engine.stop();

    console.log("✅ All tests PASSED!");
    console.log("\n🎉 ReadableStream issue is FIXED!");
    console.log("🎉 Initial prompt issue is FIXED!");
    process.exit(0);
  } catch (error) {
    console.error("\n❌ Test FAILED with error:");
    console.error(error);
    await engine.stop();
    process.exit(1);
  }
}

runTests();
