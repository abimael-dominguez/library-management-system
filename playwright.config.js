import { defineConfig, devices } from '@playwright/test';

const frontendBaseUrl = process.env.FRONTEND_BASE_URL || 'http://localhost:8080';

export default defineConfig({
  testDir: './tests/frontend',
  fullyParallel: false,
  retries: 0,
  timeout: 30000,
  expect: {
    timeout: 7000
  },
  reporter: [['list']],
  use: {
    baseURL: frontendBaseUrl,
    browserName: 'chromium',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure'
  },
  projects: [
    {
      name: 'mobile',
      use: {
        ...devices['Pixel 5'],
        viewport: { width: 390, height: 844 }
      }
    },
    {
      name: 'desktop',
      use: {
        viewport: { width: 1366, height: 900 }
      }
    }
  ]
});
