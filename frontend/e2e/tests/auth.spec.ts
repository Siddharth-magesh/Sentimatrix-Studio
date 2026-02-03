import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test.describe('Login Page', () => {
    test('should display login form', async ({ page }) => {
      await page.goto('/auth/login');

      await expect(page.getByRole('heading', { name: /sign in/i })).toBeVisible();
      await expect(page.getByLabel(/email/i)).toBeVisible();
      await expect(page.getByLabel(/password/i)).toBeVisible();
      await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
    });

    test('should show validation errors for empty form', async ({ page }) => {
      await page.goto('/auth/login');

      await page.getByRole('button', { name: /sign in/i }).click();

      await expect(page.getByText(/email is required/i)).toBeVisible();
      await expect(page.getByText(/password is required/i)).toBeVisible();
    });

    test('should show error for invalid credentials', async ({ page }) => {
      await page.goto('/auth/login');

      await page.getByLabel(/email/i).fill('invalid@example.com');
      await page.getByLabel(/password/i).fill('wrongpassword');
      await page.getByRole('button', { name: /sign in/i }).click();

      await expect(page.getByText(/invalid credentials/i)).toBeVisible();
    });

    test('should navigate to register page', async ({ page }) => {
      await page.goto('/auth/login');

      await page.getByRole('link', { name: /sign up/i }).click();

      await expect(page).toHaveURL('/auth/register');
    });

    test('should login successfully with valid credentials', async ({ page }) => {
      // This test requires a test user to be seeded
      await page.goto('/auth/login');

      await page.getByLabel(/email/i).fill('test@example.com');
      await page.getByLabel(/password/i).fill('TestPass123');
      await page.getByRole('button', { name: /sign in/i }).click();

      await expect(page).toHaveURL('/dashboard');
    });
  });

  test.describe('Register Page', () => {
    test('should display registration form', async ({ page }) => {
      await page.goto('/auth/register');

      await expect(page.getByRole('heading', { name: /create account/i })).toBeVisible();
      await expect(page.getByLabel(/name/i)).toBeVisible();
      await expect(page.getByLabel(/email/i)).toBeVisible();
      await expect(page.getByLabel(/^password$/i)).toBeVisible();
      await expect(page.getByLabel(/confirm password/i)).toBeVisible();
    });

    test('should show validation errors', async ({ page }) => {
      await page.goto('/auth/register');

      await page.getByRole('button', { name: /create account/i }).click();

      await expect(page.getByText(/name is required/i)).toBeVisible();
    });

    test('should validate password requirements', async ({ page }) => {
      await page.goto('/auth/register');

      await page.getByLabel(/^password$/i).fill('weak');

      await expect(page.getByText(/at least 8 characters/i)).toBeVisible();
    });

    test('should validate password confirmation', async ({ page }) => {
      await page.goto('/auth/register');

      await page.getByLabel(/^password$/i).fill('StrongPass123');
      await page.getByLabel(/confirm password/i).fill('DifferentPass123');
      await page.getByRole('button', { name: /create account/i }).click();

      await expect(page.getByText(/passwords do not match/i)).toBeVisible();
    });

    test('should navigate to login page', async ({ page }) => {
      await page.goto('/auth/register');

      await page.getByRole('link', { name: /sign in/i }).click();

      await expect(page).toHaveURL('/auth/login');
    });
  });

  test.describe('Protected Routes', () => {
    test('should redirect to login when not authenticated', async ({ page }) => {
      await page.goto('/dashboard');

      await expect(page).toHaveURL(/\/auth\/login/);
    });

    test('should redirect to login when accessing projects', async ({ page }) => {
      await page.goto('/dashboard/projects');

      await expect(page).toHaveURL(/\/auth\/login/);
    });
  });

  test.describe('Logout', () => {
    test.beforeEach(async ({ page }) => {
      // Login first
      await page.goto('/auth/login');
      await page.getByLabel(/email/i).fill('test@example.com');
      await page.getByLabel(/password/i).fill('TestPass123');
      await page.getByRole('button', { name: /sign in/i }).click();
      await expect(page).toHaveURL('/dashboard');
    });

    test('should logout successfully', async ({ page }) => {
      await page.getByRole('button', { name: /logout/i }).click();

      await expect(page).toHaveURL('/auth/login');
    });
  });
});
