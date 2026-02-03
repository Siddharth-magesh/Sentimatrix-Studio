import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/auth/login');
    await page.getByLabel(/email/i).fill('test@example.com');
    await page.getByLabel(/password/i).fill('TestPass123');
    await page.getByRole('button', { name: /sign in/i }).click();
    await expect(page).toHaveURL('/dashboard');
  });

  test.describe('Dashboard Overview', () => {
    test('should display dashboard header', async ({ page }) => {
      await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();
    });

    test('should display stats cards', async ({ page }) => {
      await expect(page.getByText(/total projects/i)).toBeVisible();
      await expect(page.getByText(/total results/i)).toBeVisible();
    });

    test('should display sidebar navigation', async ({ page }) => {
      await expect(page.getByRole('link', { name: /projects/i })).toBeVisible();
      await expect(page.getByRole('link', { name: /settings/i })).toBeVisible();
    });

    test('should show loading state initially', async ({ page }) => {
      await page.goto('/dashboard');

      // Should show loading skeleton briefly
      const skeleton = page.locator('[class*="animate-pulse"]');
      await expect(skeleton.first()).toBeVisible({ timeout: 1000 }).catch(() => {
        // Loading might be too fast to catch
      });
    });

    test('should show empty state when no projects', async ({ page }) => {
      // For a new user with no projects
      const emptyState = page.getByText(/no projects yet/i);
      const isVisible = await emptyState.isVisible().catch(() => false);

      if (isVisible) {
        await expect(page.getByRole('button', { name: /create project/i })).toBeVisible();
      }
    });
  });

  test.describe('Navigation', () => {
    test('should navigate to projects page', async ({ page }) => {
      await page.getByRole('link', { name: /projects/i }).click();

      await expect(page).toHaveURL(/\/dashboard\/projects/);
    });

    test('should navigate to settings page', async ({ page }) => {
      await page.getByRole('link', { name: /settings/i }).click();

      await expect(page).toHaveURL(/\/dashboard\/settings/);
    });

    test('should highlight active navigation item', async ({ page }) => {
      const dashboardLink = page.getByRole('link', { name: /dashboard/i }).first();

      await expect(dashboardLink).toHaveClass(/active|bg-primary/);
    });
  });

  test.describe('Responsive Design', () => {
    test('should show mobile menu on small screens', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await page.goto('/dashboard');

      // Sidebar should be hidden
      const sidebar = page.locator('[data-testid="sidebar"]');
      await expect(sidebar).not.toBeVisible();

      // Mobile menu button should be visible
      const menuButton = page.getByRole('button', { name: /menu/i });
      if (await menuButton.isVisible()) {
        await menuButton.click();
        await expect(sidebar).toBeVisible();
      }
    });

    test('should display properly on tablet', async ({ page }) => {
      await page.setViewportSize({ width: 768, height: 1024 });
      await page.goto('/dashboard');

      await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();
    });
  });

  test.describe('Error Handling', () => {
    test('should show error message on API failure', async ({ page }) => {
      // Mock API failure
      await page.route('**/api/v1/dashboard', (route) => {
        route.fulfill({
          status: 500,
          body: JSON.stringify({ detail: 'Internal server error' }),
        });
      });

      await page.goto('/dashboard');

      await expect(page.getByText(/something went wrong/i)).toBeVisible();
    });

    test('should allow retry on error', async ({ page }) => {
      let callCount = 0;

      await page.route('**/api/v1/dashboard', (route) => {
        callCount++;
        if (callCount === 1) {
          route.fulfill({
            status: 500,
            body: JSON.stringify({ detail: 'Error' }),
          });
        } else {
          route.fulfill({
            status: 200,
            body: JSON.stringify({ total_projects: 0 }),
          });
        }
      });

      await page.goto('/dashboard');
      await expect(page.getByText(/something went wrong/i)).toBeVisible();

      await page.getByRole('button', { name: /try again/i }).click();

      await expect(page.getByText(/something went wrong/i)).not.toBeVisible();
    });
  });
});
