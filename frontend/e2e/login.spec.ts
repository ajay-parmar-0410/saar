import { test, expect } from "@playwright/test";

test.describe("Login Page", () => {
  test("shows login form with branding", async ({ page }) => {
    await page.goto("/login");

    // Branding
    await expect(page.getByRole("heading", { name: "Saar" })).toBeVisible();
    await expect(
      page.getByText("Your daily briefing, distilled.")
    ).toBeVisible();

    // Form elements
    await expect(page.getByLabel("Email address")).toBeVisible();
    await expect(
      page.getByRole("button", { name: "Send Magic Link" })
    ).toBeVisible();
  });

  test("email input accepts text", async ({ page }) => {
    await page.goto("/login");
    const emailInput = page.getByLabel("Email address");
    await emailInput.fill("test@example.com");
    await expect(emailInput).toHaveValue("test@example.com");
  });

  test("email input has correct placeholder", async ({ page }) => {
    await page.goto("/login");
    const emailInput = page.getByLabel("Email address");
    await expect(emailInput).toHaveAttribute("placeholder", "you@example.com");
  });

  test("email input is required", async ({ page }) => {
    await page.goto("/login");
    const emailInput = page.getByLabel("Email address");
    await expect(emailInput).toHaveAttribute("required", "");
  });

  test("magic link button is clickable", async ({ page }) => {
    await page.goto("/login");
    const button = page.getByRole("button", { name: "Send Magic Link" });
    await expect(button).toBeEnabled();
  });
});
