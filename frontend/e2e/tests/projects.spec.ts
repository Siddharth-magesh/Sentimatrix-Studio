import { test, expect } from '@playwright/test';

test.describe('Projects', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/auth/login');
    await page.getByLabel(/email/i).fill('test@example.com');
    await page.getByLabel(/password/i).fill('TestPass123');
    await page.getByRole('button', { name: /sign in/i }).click();
    await expect(page).toHaveURL('/dashboard');
  });

  test.describe('Projects List', () => {
    test('should display projects page', async ({ page }) => {
      await page.goto('/dashboard/projects');

      await expect(page.getByRole('heading', { name: /projects/i })).toBeVisible();
    });

    test('should show create project button', async ({ page }) => {
      await page.goto('/dashboard/projects');

      await expect(page.getByRole('button', { name: /create project/i })).toBeVisible();
    });

    test('should show empty state when no projects', async ({ page }) => {
      // Mock empty projects response
      await page.route('**/api/v1/projects*', (route) => {
        route.fulfill({
          status: 200,
          body: JSON.stringify({ items: [], total: 0, page: 1, page_size: 20 }),
        });
      });

      await page.goto('/dashboard/projects');

      await expect(page.getByText(/no projects yet/i)).toBeVisible();
    });

    test('should display project cards', async ({ page }) => {
      // Mock projects response
      await page.route('**/api/v1/projects*', (route) => {
        if (route.request().method() === 'GET') {
          route.fulfill({
            status: 200,
            body: JSON.stringify({
              items: [
                {
                  id: '1',
                  name: 'Test Project',
                  description: 'A test project',
                  status: 'active',
                  preset: 'standard',
                  created_at: new Date().toISOString(),
                },
              ],
              total: 1,
              page: 1,
              page_size: 20,
            }),
          });
        } else {
          route.continue();
        }
      });

      await page.goto('/dashboard/projects');

      await expect(page.getByText('Test Project')).toBeVisible();
    });

    test('should filter projects by status', async ({ page }) => {
      await page.goto('/dashboard/projects');

      const statusFilter = page.getByRole('combobox', { name: /status/i });
      if (await statusFilter.isVisible()) {
        await statusFilter.selectOption('active');
        await expect(page).toHaveURL(/status=active/);
      }
    });

    test('should search projects', async ({ page }) => {
      await page.goto('/dashboard/projects');

      const searchInput = page.getByPlaceholder(/search/i);
      if (await searchInput.isVisible()) {
        await searchInput.fill('test');
        await page.waitForTimeout(500); // Debounce
        await expect(page).toHaveURL(/search=test/);
      }
    });
  });

  test.describe('Create Project', () => {
    test('should open create project modal', async ({ page }) => {
      await page.goto('/dashboard/projects');

      await page.getByRole('button', { name: /create project/i }).click();

      await expect(page.getByRole('dialog')).toBeVisible();
      await expect(page.getByText(/create new project/i)).toBeVisible();
    });

    test('should show preset options', async ({ page }) => {
      await page.goto('/dashboard/projects');
      await page.getByRole('button', { name: /create project/i }).click();

      await expect(page.getByText(/starter/i)).toBeVisible();
      await expect(page.getByText(/standard/i)).toBeVisible();
      await expect(page.getByText(/advanced/i)).toBeVisible();
    });

    test('should validate project name', async ({ page }) => {
      await page.goto('/dashboard/projects');
      await page.getByRole('button', { name: /create project/i }).click();

      await page.getByRole('button', { name: /create$/i }).click();

      await expect(page.getByText(/name is required/i)).toBeVisible();
    });

    test('should create project successfully', async ({ page }) => {
      // Mock create project
      await page.route('**/api/v1/projects', (route) => {
        if (route.request().method() === 'POST') {
          route.fulfill({
            status: 201,
            body: JSON.stringify({
              id: 'new-project-id',
              name: 'New Project',
              status: 'active',
            }),
          });
        } else {
          route.continue();
        }
      });

      await page.goto('/dashboard/projects');
      await page.getByRole('button', { name: /create project/i }).click();

      await page.getByLabel(/name/i).fill('New Project');
      await page.getByRole('button', { name: /create$/i }).click();

      await expect(page.getByText(/project created/i)).toBeVisible();
    });
  });

  test.describe('Project Detail', () => {
    test.beforeEach(async ({ page }) => {
      // Mock single project
      await page.route('**/api/v1/projects/1', (route) => {
        route.fulfill({
          status: 200,
          body: JSON.stringify({
            id: '1',
            name: 'Test Project',
            description: 'A test project',
            status: 'active',
            preset: 'standard',
            config: {
              scrapers: { platforms: ['amazon'] },
              llm: { provider: 'groq' },
              analysis: { sentiment: true },
            },
          }),
        });
      });
    });

    test('should display project details', async ({ page }) => {
      await page.goto('/dashboard/projects/1');

      await expect(page.getByRole('heading', { name: 'Test Project' })).toBeVisible();
    });

    test('should show project tabs', async ({ page }) => {
      await page.goto('/dashboard/projects/1');

      await expect(page.getByRole('tab', { name: /overview/i })).toBeVisible();
      await expect(page.getByRole('tab', { name: /targets/i })).toBeVisible();
      await expect(page.getByRole('tab', { name: /results/i })).toBeVisible();
      await expect(page.getByRole('tab', { name: /settings/i })).toBeVisible();
    });

    test('should navigate between tabs', async ({ page }) => {
      await page.goto('/dashboard/projects/1');

      await page.getByRole('tab', { name: /targets/i }).click();
      await expect(page.getByText(/add target/i)).toBeVisible();

      await page.getByRole('tab', { name: /results/i }).click();
      await expect(page.getByText(/results/i)).toBeVisible();
    });
  });

  test.describe('Project Actions', () => {
    test('should delete project with confirmation', async ({ page }) => {
      await page.route('**/api/v1/projects/1', (route) => {
        if (route.request().method() === 'DELETE') {
          route.fulfill({ status: 204 });
        } else {
          route.fulfill({
            status: 200,
            body: JSON.stringify({ id: '1', name: 'Test Project' }),
          });
        }
      });

      await page.goto('/dashboard/projects/1');

      await page.getByRole('button', { name: /delete/i }).click();

      // Confirmation dialog
      await expect(page.getByText(/are you sure/i)).toBeVisible();
      await page.getByRole('button', { name: /confirm/i }).click();

      await expect(page).toHaveURL('/dashboard/projects');
    });

    test('should run scrape job', async ({ page }) => {
      await page.route('**/api/v1/projects/1/scrape', (route) => {
        route.fulfill({
          status: 202,
          body: JSON.stringify({ id: 'job-1', status: 'queued' }),
        });
      });

      await page.goto('/dashboard/projects/1');

      await page.getByRole('button', { name: /run scrape/i }).click();

      await expect(page.getByText(/scrape job started/i)).toBeVisible();
    });
  });
});
