import { test, expect } from '@playwright/test';

test.describe('Export', () => {
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
          status: 'active',
          stats: { total_results: 100 },
        }),
      });
    });

    // Mock results data
    await page.route('**/api/v1/projects/1/results*', (route) => {
      if (!route.request().url().includes('export')) {
        route.fulfill({
          status: 200,
          body: JSON.stringify({
            items: [
              {
                id: 'result-1',
                content: { text: 'Great product!' },
                analysis: { sentiment: { label: 'positive' } },
                platform: 'amazon',
              },
            ],
            total: 100,
            page: 1,
            pages: 5,
          }),
        });
      } else {
        route.continue();
      }
    });
  });

  test.describe('CSV Export', () => {
    test('should export results as CSV', async ({ page }) => {
      // Mock CSV export
      await page.route('**/api/v1/projects/1/results/export?format=csv', (route) => {
        route.fulfill({
          status: 200,
          headers: {
            'Content-Type': 'text/csv',
            'Content-Disposition': 'attachment; filename="results.csv"',
          },
          body: 'id,content,sentiment,platform\nresult-1,Great product!,positive,amazon',
        });
      });

      await page.goto('/dashboard/projects/1');
      await page.getByRole('tab', { name: /results/i }).click();

      // Start waiting for download before clicking
      const downloadPromise = page.waitForEvent('download');

      await page.getByRole('button', { name: /export/i }).click();
      await page.getByRole('menuitem', { name: /csv/i }).click();

      const download = await downloadPromise;
      expect(download.suggestedFilename()).toContain('.csv');
    });

    test('should show export button in results tab', async ({ page }) => {
      await page.goto('/dashboard/projects/1');
      await page.getByRole('tab', { name: /results/i }).click();

      await expect(page.getByRole('button', { name: /export/i })).toBeVisible();
    });
  });

  test.describe('JSON Export', () => {
    test('should export results as JSON', async ({ page }) => {
      // Mock JSON export
      await page.route('**/api/v1/projects/1/results/export?format=json', (route) => {
        route.fulfill({
          status: 200,
          headers: {
            'Content-Type': 'application/json',
            'Content-Disposition': 'attachment; filename="results.json"',
          },
          body: JSON.stringify({
            project: 'Test Project',
            results: [{ id: 'result-1', content: 'Great product!' }],
          }),
        });
      });

      await page.goto('/dashboard/projects/1');
      await page.getByRole('tab', { name: /results/i }).click();

      const downloadPromise = page.waitForEvent('download');

      await page.getByRole('button', { name: /export/i }).click();
      await page.getByRole('menuitem', { name: /json/i }).click();

      const download = await downloadPromise;
      expect(download.suggestedFilename()).toContain('.json');
    });
  });

  test.describe('Excel Export', () => {
    test('should export results as XLSX', async ({ page }) => {
      // Mock XLSX export
      await page.route('**/api/v1/projects/1/results/export?format=xlsx', (route) => {
        route.fulfill({
          status: 200,
          headers: {
            'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'Content-Disposition': 'attachment; filename="results.xlsx"',
          },
          body: Buffer.from('mock xlsx content'),
        });
      });

      await page.goto('/dashboard/projects/1');
      await page.getByRole('tab', { name: /results/i }).click();

      const downloadPromise = page.waitForEvent('download');

      await page.getByRole('button', { name: /export/i }).click();
      await page.getByRole('menuitem', { name: /excel|xlsx/i }).click();

      const download = await downloadPromise;
      expect(download.suggestedFilename()).toContain('.xlsx');
    });
  });

  test.describe('Export with Filters', () => {
    test('should export filtered results only', async ({ page }) => {
      let exportUrl = '';

      await page.route('**/api/v1/projects/1/results/export*', (route) => {
        exportUrl = route.request().url();
        route.fulfill({
          status: 200,
          headers: {
            'Content-Type': 'text/csv',
            'Content-Disposition': 'attachment; filename="results.csv"',
          },
          body: 'filtered data',
        });
      });

      await page.goto('/dashboard/projects/1?sentiment=positive');
      await page.getByRole('tab', { name: /results/i }).click();

      const downloadPromise = page.waitForEvent('download');

      await page.getByRole('button', { name: /export/i }).click();
      await page.getByRole('menuitem', { name: /csv/i }).click();

      await downloadPromise;

      // Verify filter was included in export request
      expect(exportUrl).toContain('sentiment=positive');
    });

    test('should export with date range filter', async ({ page }) => {
      let exportUrl = '';

      await page.route('**/api/v1/projects/1/results/export*', (route) => {
        exportUrl = route.request().url();
        route.fulfill({
          status: 200,
          body: 'data',
        });
      });

      await page.goto('/dashboard/projects/1?start_date=2024-01-01&end_date=2024-01-31');
      await page.getByRole('tab', { name: /results/i }).click();

      const downloadPromise = page.waitForEvent('download');

      await page.getByRole('button', { name: /export/i }).click();
      await page.getByRole('menuitem', { name: /csv/i }).click();

      await downloadPromise;

      expect(exportUrl).toContain('start_date=2024-01-01');
      expect(exportUrl).toContain('end_date=2024-01-31');
    });
  });

  test.describe('Export Error Handling', () => {
    test('should show error toast on export failure', async ({ page }) => {
      await page.route('**/api/v1/projects/1/results/export*', (route) => {
        route.fulfill({
          status: 500,
          body: JSON.stringify({ detail: 'Export failed' }),
        });
      });

      await page.goto('/dashboard/projects/1');
      await page.getByRole('tab', { name: /results/i }).click();

      await page.getByRole('button', { name: /export/i }).click();
      await page.getByRole('menuitem', { name: /csv/i }).click();

      await expect(page.getByText(/export failed/i)).toBeVisible();
    });

    test('should disable export when no results', async ({ page }) => {
      await page.route('**/api/v1/projects/1/results*', (route) => {
        if (!route.request().url().includes('export')) {
          route.fulfill({
            status: 200,
            body: JSON.stringify({ items: [], total: 0, page: 1, pages: 0 }),
          });
        }
      });

      await page.goto('/dashboard/projects/1');
      await page.getByRole('tab', { name: /results/i }).click();

      const exportButton = page.getByRole('button', { name: /export/i });
      await expect(exportButton).toBeDisabled();
    });
  });

  test.describe('Global Results Export', () => {
    test.beforeEach(async ({ page }) => {
      await page.route('**/api/v1/results*', (route) => {
        if (!route.request().url().includes('export')) {
          route.fulfill({
            status: 200,
            body: JSON.stringify({
              items: [
                { id: '1', content: { text: 'Result 1' }, project_id: '1' },
                { id: '2', content: { text: 'Result 2' }, project_id: '2' },
              ],
              total: 200,
              page: 1,
              pages: 10,
            }),
          });
        } else {
          route.fulfill({
            status: 200,
            headers: {
              'Content-Type': 'text/csv',
            },
            body: 'csv data',
          });
        }
      });
    });

    test('should export all results from global results page', async ({ page }) => {
      await page.goto('/dashboard/results');

      const downloadPromise = page.waitForEvent('download');

      await page.getByRole('button', { name: /export/i }).click();
      await page.getByRole('menuitem', { name: /csv/i }).click();

      const download = await downloadPromise;
      expect(download).toBeTruthy();
    });

    test('should filter by project before export', async ({ page }) => {
      let exportUrl = '';

      await page.route('**/api/v1/results/export*', (route) => {
        exportUrl = route.request().url();
        route.fulfill({
          status: 200,
          body: 'data',
        });
      });

      await page.goto('/dashboard/results?project_id=1');

      const downloadPromise = page.waitForEvent('download');

      await page.getByRole('button', { name: /export/i }).click();
      await page.getByRole('menuitem', { name: /csv/i }).click();

      await downloadPromise;

      expect(exportUrl).toContain('project_id=1');
    });
  });
});
