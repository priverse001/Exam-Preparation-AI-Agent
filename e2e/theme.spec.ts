/**
 * Test 2 — Dark / Light theme toggle.
 */
import { test, expect } from "@playwright/test";

test.describe("Theme Toggle", () => {
  test("toggles between light and dark mode", async ({ page }) => {
    await page.goto("/");
    const html = page.locator("html");

    // Should start in light mode (no "dark" class)
    await expect(html).not.toHaveClass(/dark/);

    // Click theme toggle
    await page.getByRole("button", { name: "Toggle theme" }).click();

    // Should now be in dark mode
    await expect(html).toHaveClass(/dark/);

    // Background should be dark
    const bg = await page.locator("div.flex.h-screen").evaluate(
      (el) => getComputedStyle(el).backgroundColor
    );
    // Dark mode bg is gray-900 ≈ rgb(17, 24, 39)
    expect(bg).toMatch(/rgb\(17, 24, 39\)/);

    // Toggle back
    await page.getByRole("button", { name: "Toggle theme" }).click();
    await expect(html).not.toHaveClass(/dark/);
  });
});
