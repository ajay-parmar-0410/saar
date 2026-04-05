import { test, expect } from "@playwright/test";

test.describe("Navigation", () => {
  test("login page loads", async ({ page }) => {
    await page.goto("/login");
    await expect(page).toHaveURL(/login/);
    await expect(page.getByRole("heading", { name: "Saar" })).toBeVisible();
  });

  test("root shows landing page with Get Started", async ({ page }) => {
    await page.goto("/");
    // Landing page shows branding and CTA
    await expect(page.getByRole("heading", { name: "Saar" })).toBeVisible();
    await expect(
      page.getByRole("link", { name: "Get Started" }).first()
    ).toBeVisible();
  });

  test("protected routes redirect to login when unauthenticated", async ({
    page,
  }) => {
    // Try accessing briefing without auth
    await page.goto("/briefing");
    // Should end up at login
    await page.waitForURL(/\/login/, { timeout: 10000 });
    await expect(page).toHaveURL(/login/);
  });

  test("onboarding page exists", async ({ page }) => {
    const response = await page.goto("/onboarding");
    // Should return a page (even if it redirects)
    expect(response?.status()).toBeLessThan(500);
  });
});
