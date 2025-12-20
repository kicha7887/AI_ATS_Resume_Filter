# Vercel Speed Insights Setup Guide

This project has been configured to use **Vercel Speed Insights** for performance monitoring.

## What is Vercel Speed Insights?

Vercel Speed Insights is a tool that helps you understand your application's real-world performance metrics by collecting data on Core Web Vitals and other performance indicators.

## Setup Steps

### 1. Prerequisites

- A Vercel account ([sign up for free](https://vercel.com/signup) if you don't have one)
- The Vercel CLI installed:

```bash
npm install -g vercel
# or
pnpm install -g vercel
```

### 2. Enable Speed Insights in Vercel Dashboard

1. Go to your [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project (or create a new one)
3. Go to the **Speed Insights** tab
4. Click **Enable** to activate Speed Insights

> **Note:** Enabling Speed Insights will add new routes at `/_vercel/speed-insights/*` after your next deployment.

### 3. Deploy to Vercel

Deploy your Streamlit app to Vercel:

```bash
vercel deploy
```

Alternatively, connect your repository to Vercel for automatic deployments:
- Go to [Vercel Import](https://vercel.com/import)
- Connect your Git repository
- Vercel will automatically deploy on every push

### 4. View Your Data

Once deployed and users have visited your site:

1. Go to your [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project
3. Click the **Speed Insights** tab
4. After a few days of visitor traffic, you'll see metrics and analytics

## Integration Details

### How It Works

This project uses HTML-based Speed Insights injection for Streamlit compatibility:

```html
<script>
    window.si = window.si || function () { (window.siq = window.siq || []).push(arguments); };
</script>
<script defer src="/_vercel/speed-insights/script.js"></script>
```

This script:
- Tracks Core Web Vitals (Largest Contentful Paint, First Input Delay, Cumulative Layout Shift)
- Collects real-world performance data from users
- Sends data to Vercel for analysis (after deployment)

### Deployment Configuration

The `vercel.json` file configures deployment settings for this Streamlit app:
- Specifies the build command
- Configures the development environment
- Sets the framework type

## Metrics You'll See

Speed Insights tracks several important metrics:

- **Largest Contentful Paint (LCP):** Time until the largest content element is rendered
- **First Input Delay (FID):** Responsiveness of the page to user interactions
- **Cumulative Layout Shift (CLS):** Visual stability of the page
- **Time to First Byte (TTFB):** Server response time
- **First Contentful Paint (FCP):** Time until content starts appearing

## Privacy & Data Compliance

Vercel Speed Insights is designed with privacy in mind:
- Data is aggregated and anonymized
- No personal information is collected
- You can filter sensitive URL patterns if needed
- For more details, see [Vercel's Privacy Policy](https://vercel.com/docs/speed-insights/privacy-policy)

## Troubleshooting

### Script Not Loading

If the Speed Insights script doesn't load (`/_vercel/speed-insights/script.js`):

1. Verify deployment completed successfully
2. Check that Speed Insights is enabled in the Vercel dashboard
3. Wait a few minutes after enabling (propagation takes time)
4. Clear your browser cache and reload

### No Data Appearing

- Give it time: data collection takes a few hours to a few days depending on traffic
- Ensure the script is loading (check browser DevTools Network tab)
- Verify the project is getting real user traffic

## Next Steps

- [Learn more about Vercel Speed Insights](https://vercel.com/docs/speed-insights)
- [Explore metrics and optimization tips](https://vercel.com/docs/speed-insights/metrics)
- [Review Vercel's performance best practices](https://vercel.com/docs/concepts/performance)

## Additional Resources

- [Vercel Speed Insights Documentation](https://vercel.com/docs/speed-insights)
- [Core Web Vitals Guide](https://web.dev/vitals/)
- [Web Performance Best Practices](https://web.dev/performance/)
