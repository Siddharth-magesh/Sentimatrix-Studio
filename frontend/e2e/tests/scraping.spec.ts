import { test, expect } from '@playwright/test';

test.describe('Scraping', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/auth/login');
    await page.getByLabel(/email/i).fill('test@example.com');
    await page.getByLabel(/password/i).fill('TestPass123');
    await page.getByRole('button', { name: /sign in/i }).click();
    await expect(page).toHaveURL('/dashboard');

    // Mock project data
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
            scrapers: { platforms: ['amazon', 'steam'] },
            llm: { provider: 'groq', model: 'llama-3.3-70b-versatile' },
            analysis: { sentiment: true, emotions: true },
          },
          stats: {
            total_targets: 5,
            total_results: 100,
            last_scrape_at: new Date().toISOString(),
          },
        }),
      });
    });
  });

  test.describe('Targets Management', () => {
    test.beforeEach(async ({ page }) => {
      // Mock targets data
      await page.route('**/api/v1/projects/1/targets*', (route) => {
        if (route.request().method() === 'GET') {
          route.fulfill({
            status: 200,
            body: JSON.stringify([
              {
                id: 'target-1',
                url: 'https://amazon.com/product/123',
                platform: 'amazon',
                status: 'pending',
                scrape_count: 0,
              },
              {
                id: 'target-2',
                url: 'https://store.steampowered.com/app/456',
                platform: 'steam',
                status: 'scraped',
                scrape_count: 5,
              },
            ]),
          });
        } else {
          route.continue();
        }
      });
    });

    test('should display targets list', async ({ page }) => {
      await page.goto('/dashboard/projects/1');
      await page.getByRole('tab', { name: /targets/i }).click();

      await expect(page.getByText('https://amazon.com/product/123')).toBeVisible();
      await expect(page.getByText('https://store.steampowered.com/app/456')).toBeVisible();
    });

    test('should show target status badges', async ({ page }) => {
      await page.goto('/dashboard/projects/1');
      await page.getByRole('tab', { name: /targets/i }).click();

      await expect(page.getByText(/pending/i)).toBeVisible();
      await expect(page.getByText(/scraped/i)).toBeVisible();
    });

    test('should open add target modal', async ({ page }) => {
      await page.goto('/dashboard/projects/1');
      await page.getByRole('tab', { name: /targets/i }).click();

      await page.getByRole('button', { name: /add target/i }).click();

      await expect(page.getByRole('dialog')).toBeVisible();
      await expect(page.getByLabel(/url/i)).toBeVisible();
    });

    test('should add new target', async ({ page }) => {
      await page.route('**/api/v1/projects/1/targets', (route) => {
        if (route.request().method() === 'POST') {
          route.fulfill({
            status: 201,
            body: JSON.stringify({
              id: 'target-3',
              url: 'https://amazon.com/product/789',
              platform: 'amazon',
              status: 'pending',
            }),
          });
        } else {
          route.continue();
        }
      });

      await page.goto('/dashboard/projects/1');
      await page.getByRole('tab', { name: /targets/i }).click();
      await page.getByRole('button', { name: /add target/i }).click();

      await page.getByLabel(/url/i).fill('https://amazon.com/product/789');
      await page.getByRole('button', { name: /add$/i }).click();

      await expect(page.getByText(/target added/i)).toBeVisible();
    });

    test('should validate target URL', async ({ page }) => {
      await page.goto('/dashboard/projects/1');
      await page.getByRole('tab', { name: /targets/i }).click();
      await page.getByRole('button', { name: /add target/i }).click();

      await page.getByLabel(/url/i).fill('not-a-valid-url');
      await page.getByRole('button', { name: /add$/i }).click();

      await expect(page.getByText(/valid url/i)).toBeVisible();
    });

    test('should bulk add targets', async ({ page }) => {
      await page.route('**/api/v1/projects/1/targets/bulk', (route) => {
        route.fulfill({
          status: 201,
          body: JSON.stringify([
            { id: 'target-4', url: 'https://amazon.com/product/111', status: 'pending' },
            { id: 'target-5', url: 'https://amazon.com/product/222', status: 'pending' },
          ]),
        });
      });

      await page.goto('/dashboard/projects/1');
      await page.getByRole('tab', { name: /targets/i }).click();
      await page.getByRole('button', { name: /bulk add/i }).click();

      await page.getByRole('textbox').fill(`https://amazon.com/product/111
https://amazon.com/product/222`);
      await page.getByRole('button', { name: /add targets/i }).click();

      await expect(page.getByText(/2 targets added/i)).toBeVisible();
    });

    test('should delete target', async ({ page }) => {
      await page.route('**/api/v1/projects/1/targets/target-1', (route) => {
        if (route.request().method() === 'DELETE') {
          route.fulfill({ status: 204 });
        } else {
          route.continue();
        }
      });

      await page.goto('/dashboard/projects/1');
      await page.getByRole('tab', { name: /targets/i }).click();

      // Find and click delete button for first target
      const targetRow = page.getByText('https://amazon.com/product/123').locator('..').locator('..');
      await targetRow.getByRole('button', { name: /delete/i }).click();

      // Confirm deletion
      await page.getByRole('button', { name: /confirm/i }).click();

      await expect(page.getByText(/target deleted/i)).toBeVisible();
    });
  });

  test.describe('Scrape Jobs', () => {
    test('should start scrape job', async ({ page }) => {
      await page.route('**/api/v1/projects/1/scrape', (route) => {
        route.fulfill({
          status: 202,
          body: JSON.stringify({
            id: 'job-1',
            project_id: '1',
            status: 'queued',
            progress: 0,
          }),
        });
      });

      await page.goto('/dashboard/projects/1');
      await page.getByRole('button', { name: /run scrape/i }).click();

      await expect(page.getByText(/scrape job started/i)).toBeVisible();
    });

    test('should show running job progress', async ({ page }) => {
      await page.route('**/api/v1/projects/1/scrape/jobs*', (route) => {
        route.fulfill({
          status: 200,
          body: JSON.stringify([
            {
              id: 'job-1',
              project_id: '1',
              status: 'running',
              progress: 50,
              stats: {
                targets_processed: 2,
                results_scraped: 45,
                errors: 0,
              },
              started_at: new Date().toISOString(),
            },
          ]),
        });
      });

      await page.goto('/dashboard/projects/1');

      await expect(page.getByText(/running/i)).toBeVisible();
      await expect(page.getByText(/50%/)).toBeVisible();
    });

    test('should cancel running job', async ({ page }) => {
      await page.route('**/api/v1/projects/1/scrape/jobs*', (route) => {
        if (route.request().method() === 'GET') {
          route.fulfill({
            status: 200,
            body: JSON.stringify([
              { id: 'job-1', status: 'running', progress: 30 },
            ]),
          });
        } else {
          route.continue();
        }
      });

      await page.route('**/api/v1/projects/1/scrape/jobs/job-1/cancel', (route) => {
        route.fulfill({
          status: 200,
          body: JSON.stringify({ id: 'job-1', status: 'cancelled' }),
        });
      });

      await page.goto('/dashboard/projects/1');
      await page.getByRole('button', { name: /cancel/i }).click();

      await expect(page.getByText(/job cancelled/i)).toBeVisible();
    });

    test('should display completed job stats', async ({ page }) => {
      await page.route('**/api/v1/projects/1/scrape/jobs*', (route) => {
        route.fulfill({
          status: 200,
          body: JSON.stringify([
            {
              id: 'job-1',
              project_id: '1',
              status: 'completed',
              progress: 100,
              stats: {
                targets_processed: 5,
                results_scraped: 150,
                errors: 2,
              },
              started_at: '2024-01-01T10:00:00Z',
              completed_at: '2024-01-01T10:15:00Z',
            },
          ]),
        });
      });

      await page.goto('/dashboard/projects/1');

      await expect(page.getByText(/completed/i)).toBeVisible();
      await expect(page.getByText(/150 results/i)).toBeVisible();
    });

    test('should show job error details', async ({ page }) => {
      await page.route('**/api/v1/projects/1/scrape/jobs*', (route) => {
        route.fulfill({
          status: 200,
          body: JSON.stringify([
            {
              id: 'job-1',
              status: 'failed',
              progress: 25,
              error: 'Rate limit exceeded',
              stats: { errors: 5 },
            },
          ]),
        });
      });

      await page.goto('/dashboard/projects/1');

      await expect(page.getByText(/failed/i)).toBeVisible();
      await expect(page.getByText(/rate limit/i)).toBeVisible();
    });
  });

  test.describe('Results View', () => {
    test.beforeEach(async ({ page }) => {
      await page.route('**/api/v1/projects/1/results*', (route) => {
        route.fulfill({
          status: 200,
          body: JSON.stringify({
            items: [
              {
                id: 'result-1',
                content: { text: 'Great product!', rating: 5 },
                analysis: {
                  sentiment: { label: 'positive', confidence: 0.95 },
                  emotions: { joy: 0.8, trust: 0.6 },
                },
                platform: 'amazon',
                created_at: new Date().toISOString(),
              },
              {
                id: 'result-2',
                content: { text: 'Not worth the price.', rating: 2 },
                analysis: {
                  sentiment: { label: 'negative', confidence: 0.87 },
                  emotions: { anger: 0.5, disappointment: 0.7 },
                },
                platform: 'steam',
                created_at: new Date().toISOString(),
              },
            ],
            total: 2,
            page: 1,
            pages: 1,
          }),
        });
      });
    });

    test('should display results table', async ({ page }) => {
      await page.goto('/dashboard/projects/1');
      await page.getByRole('tab', { name: /results/i }).click();

      await expect(page.getByText('Great product!')).toBeVisible();
      await expect(page.getByText('Not worth the price.')).toBeVisible();
    });

    test('should show sentiment badges', async ({ page }) => {
      await page.goto('/dashboard/projects/1');
      await page.getByRole('tab', { name: /results/i }).click();

      await expect(page.getByText(/positive/i)).toBeVisible();
      await expect(page.getByText(/negative/i)).toBeVisible();
    });

    test('should filter results by sentiment', async ({ page }) => {
      await page.goto('/dashboard/projects/1');
      await page.getByRole('tab', { name: /results/i }).click();

      const sentimentFilter = page.getByRole('combobox', { name: /sentiment/i });
      if (await sentimentFilter.isVisible()) {
        await sentimentFilter.selectOption('positive');
        await expect(page).toHaveURL(/sentiment=positive/);
      }
    });

    test('should open result detail modal', async ({ page }) => {
      await page.goto('/dashboard/projects/1');
      await page.getByRole('tab', { name: /results/i }).click();

      await page.getByText('Great product!').click();

      await expect(page.getByRole('dialog')).toBeVisible();
      await expect(page.getByText(/95%/)).toBeVisible(); // Confidence
    });

    test('should delete result', async ({ page }) => {
      await page.route('**/api/v1/projects/1/results/result-1', (route) => {
        if (route.request().method() === 'DELETE') {
          route.fulfill({ status: 204 });
        } else {
          route.continue();
        }
      });

      await page.goto('/dashboard/projects/1');
      await page.getByRole('tab', { name: /results/i }).click();

      const resultRow = page.getByText('Great product!').locator('..').locator('..');
      await resultRow.getByRole('button', { name: /delete/i }).click();
      await page.getByRole('button', { name: /confirm/i }).click();

      await expect(page.getByText(/result deleted/i)).toBeVisible();
    });
  });
});
