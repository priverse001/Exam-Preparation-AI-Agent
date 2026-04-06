import { defineConfig } from "@playwright/test";

/**
 * Playwright config for the Study Assistant AI workshop E2E tests.
 *
 * Usage:
 *   npx playwright test                          # headless (CI)
 *   npx playwright test --headed                 # headful (demo / local dev)
 *   npx playwright test --ui                     # interactive Playwright UI
 *   npx playwright test --project=demo --headed  # run ONLY the demo walkthrough, headful
 *
 * The app (npm run start) must already be running on ports 5173 + 8002.
 *
 * Execution order:
 *   1. "setup"  — health check, delete all docs/notes, upload 5 sample docs
 *   2. "tests"  — all other specs (depends on setup completing first)
 *   3. "demo"   — standalone full walkthrough (runs its own setup, no deps)
 */
const isHeaded = process.argv.includes("--headed");
const projectArg = process.argv.find((arg) => arg.startsWith("--project="));
const projectFlagIndex = process.argv.indexOf("--project");
const requestedProjectName =
  projectArg?.split("=", 2)[1] ?? (projectFlagIndex >= 0 ? process.argv[projectFlagIndex + 1] : null);
const includeDemoProject = requestedProjectName === "demo";

const projects = [
  {
    name: "setup",
    testMatch: "setup.spec.ts",
  },
  {
    name: "tests",
    testIgnore: ["setup.spec.ts", "demo-walkthrough.spec.ts"],
    dependencies: ["setup"],
  },
];

if (includeDemoProject) {
  projects.push({
    name: "demo",
    testMatch: "demo-walkthrough.spec.ts",
  });
}

export default defineConfig({
  testDir: "./e2e",
  timeout: 180_000, // agent responses can take a while
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
    // Slow down every Playwright action by 600ms in headed mode
    // so you can actually watch what's happening
    ...(isHeaded ? { launchOptions: { slowMo: 600 } } : {}),
  },
  projects,
});
