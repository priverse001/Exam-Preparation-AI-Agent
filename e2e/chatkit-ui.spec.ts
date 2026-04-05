/**
 * Test 5 — ChatKit UI elements: welcome screen, prompt buttons, history.
 */
import { test, expect } from "@playwright/test";
import { chatFrame, startNewChat } from "./helpers";

test.describe("ChatKit UI", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await expect(
      chatFrame(page).getByRole("heading", { name: /welcome/i })
    ).toBeVisible({ timeout: 15_000 });
  });

  test("welcome screen shows greeting and prompt buttons", async ({ page }) => {
    const frame = chatFrame(page);

    await expect(
      frame.getByRole("heading", { name: "Welcome to your AI Study Assistant!" })
    ).toBeVisible();

    // Three starter prompt buttons
    await expect(frame.getByRole("button", { name: "Summarize my documents" })).toBeVisible();
    await expect(frame.getByRole("button", { name: "Explain a concept" })).toBeVisible();
    await expect(frame.getByRole("button", { name: "Create revision notes" })).toBeVisible();
  });

  test("chat input placeholder is correct", async ({ page }) => {
    const input = chatFrame(page).getByRole("textbox", { name: /ask about your study/i });
    await expect(input).toBeVisible();
  });

  test("disclaimer text is shown", async ({ page }) => {
    await expect(
      chatFrame(page).getByText(/answers are grounded/i)
    ).toBeVisible();
  });

  test("clicking a prompt button sends the message", async ({ page }) => {
    const frame = chatFrame(page);

    // Click "Explain a concept" prompt
    await frame.getByRole("button", { name: "Explain a concept" }).click();

    // Should start a conversation — an article with user message should appear
    await expect(
      frame.locator("article").first()
    ).toBeVisible({ timeout: 10_000 });
  });

  test("conversation history button is visible", async ({ page }) => {
    await expect(
      chatFrame(page).getByRole("button", { name: "Conversation history" })
    ).toBeVisible();
  });
});
