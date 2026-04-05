import { defineConfig } from "@playwright/test";

/**
 * Playwright config for the Study Assistant AI workshop E2E tests.
 *
 * Usage:
 *   npx playwright test              # headless (CI)
 *   npx playwright test --headed     # headful (demo / local dev)
 *   npx playwright test --ui         # interactive Playwright UI
 *
 * The app (npm run start) must already be running on ports 5173 + 8002.
 *
 * Execution order:
 *   1. "setup"  — health check, delete all docs/notes, upload 5 sample docs
 *   2. "tests"  — all other specs (depends on setup completing first)
 */
export default defineConfig({
  testDir: "./e2e",
  timeout: 120_000, // agent responses can take a while
  expect: { timeout: 30_000 },
  retries: 0,
  workers: 1, // serial — tests share state (uploaded docs)
  reporter: [["html", { open: "never" }], ["list"]],
  use: {
    baseURL: "http://localhost:5173",
    headless: true,
    viewport: { width: 1280, height: 720 },
    screenshot: "only-on-failure",
    trace: "retain-on-failure",
  },
  projects: [
    {
      name: "setup",
      testMatch: "setup.spec.ts",
    },
    {
      name: "tests",
      testIgnore: "setup.spec.ts",
      dependencies: ["setup"],
    },
  ],
});
