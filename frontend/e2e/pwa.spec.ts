import { test, expect } from "@playwright/test";

test.describe("PWA", () => {
  test("has a web manifest", async ({ page }) => {
    await page.goto("/login");
    const manifest = page.locator('link[rel="manifest"]');
    await expect(manifest).toHaveCount(1);
  });

  test("has viewport meta tag for mobile", async ({ page }) => {
    await page.goto("/login");
    const viewport = page.locator('meta[name="viewport"]');
    await expect(viewport).toHaveCount(1);
  });

  test("pages are mobile-friendly (no horizontal scroll)", async ({ page }) => {
    await page.goto("/login");
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    const viewportWidth = await page.evaluate(() => window.innerWidth);
    expect(bodyWidth).toBeLessThanOrEqual(viewportWidth + 1); // +1 for rounding
  });
});
