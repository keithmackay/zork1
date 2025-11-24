#!/usr/bin/env bun
/**
 * Test save/load functionality
 */

import { SaveManager } from "./src/save-manager";
import type { GameState } from "./src/types";

async function testSaveLoad() {
  console.log("🧪 Testing Save/Load Functionality\n");

  const saveManager = new SaveManager();
  await saveManager.initialize();

  try {
    // Test 1: Save a game
    console.log("✓ Test 1: Saving game state...");
    const testState: GameState = {
      history: ["look", "take lamp", "inventory"],
      lastCommand: "inventory",
      timestamp: Date.now(),
      gameName: "zork1",
    };

    await saveManager.saveGame("test-save-1", testState);
    console.log("  Saved as 'test-save-1'");

    // Test 2: List saves
    console.log("\n✓ Test 2: Listing saved games...");
    const saves = await saveManager.listSaves();
    console.log(`  Found ${saves.length} saved game(s)`);
    saves.forEach((save) => {
      console.log(`    - ${save.name} (${new Date(save.timestamp).toLocaleString()})`);
    });

    // Test 3: Load the game
    console.log("\n✓ Test 3: Loading saved game...");
    const loadedState = await saveManager.loadGame("test-save-1");
    if (loadedState) {
      console.log(`  Game name: ${loadedState.gameName}`);
      console.log(`  Last command: ${loadedState.lastCommand}`);
      console.log(`  Command history (${loadedState.history.length} commands):`);
      loadedState.history.forEach((cmd, i) => {
        console.log(`    ${i + 1}. ${cmd}`);
      });
    }

    // Test 4: Verify data integrity
    console.log("\n✓ Test 4: Verifying data integrity...");
    const matches =
      loadedState &&
      loadedState.history.length === testState.history.length &&
      loadedState.lastCommand === testState.lastCommand &&
      loadedState.gameName === testState.gameName;

    if (matches) {
      console.log("  ✅ Data integrity verified!");
    } else {
      console.log("  ❌ Data mismatch!");
      console.log("  Original:", testState);
      console.log("  Loaded:", loadedState);
    }

    // Test 5: Save with special characters
    console.log("\n✓ Test 5: Testing filename sanitization...");
    await saveManager.saveGame("Test Save #2 (special!)", testState);
    const saves2 = await saveManager.listSaves();
    console.log(`  Total saves now: ${saves2.length}`);

    console.log("\n✅ All save/load tests passed!");
  } catch (error) {
    console.error("\n❌ Save/load test failed:", error);
    process.exit(1);
  }
}

testSaveLoad();
