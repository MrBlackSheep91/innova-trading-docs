# InnovaTrading API Documentation

Professional API documentation powered by [Mintlify](https://mintlify.com).

## Local Development

### Prerequisites

- Node.js 18+
- npm or yarn

### Install Mintlify CLI

```bash
npm i -g mintlify
```

### Run locally

```bash
cd docs-site
mintlify dev
```

Open http://localhost:3000 to see the docs.

## Deployment

### Option 1: Mintlify Hosting (Recommended)

1. Go to [mintlify.com](https://mintlify.com) and sign up
2. Connect your GitHub repository
3. Set the docs directory to `docs-site`
4. Configure custom domain: `docs.innova-trading.com`

### Option 2: Manual Build

```bash
# Build static files
mintlify build

# Output is in .mintlify/output
```

### Option 3: Vercel/Netlify

1. Fork or push to GitHub
2. Connect to Vercel/Netlify
3. Build command: `cd docs-site && npx mintlify build`
4. Output directory: `docs-site/.mintlify/output`

## Custom Domain Setup

To use `docs.innova-trading.com`:

1. Add CNAME record in your DNS:
   ```
   docs.innova-trading.com -> cname.mintlify.com
   ```

2. Configure in Mintlify dashboard under Settings > Domains

## Structure

```
docs-site/
├── mint.json              # Main configuration
├── introduction.mdx       # Welcome page
├── quickstart.mdx         # 5-minute guide
├── authentication.mdx     # API key docs
├── api-reference/         # API endpoints
│   ├── introduction.mdx
│   ├── market-data/
│   │   ├── get-bars.mdx
│   │   └── get-symbols.mdx
│   └── indicators/
│       ├── submit-indicator.mdx
│       ├── get-indicator.mdx
│       ├── delete-indicator.mdx
│       └── list-indicators.mdx
├── concepts/              # Core concepts
│   ├── signals.mdx
│   ├── indicators.mdx
│   └── timeframes.mdx
├── sdks/                  # SDK documentation
│   ├── overview.mdx
│   ├── python.mdx
│   └── javascript.mdx
├── guides/                # How-to guides
│   ├── first-indicator.mdx
│   ├── signal-best-practices.mdx
│   └── continuous-integration.mdx
└── logo/                  # Branding
    ├── dark.svg
    └── light.svg
```

## Adding New Pages

1. Create a new `.mdx` file in the appropriate directory
2. Add frontmatter:
   ```mdx
   ---
   title: 'Page Title'
   description: 'Page description'
   ---
   ```
3. Add the page to `mint.json` navigation

## API Endpoint Documentation

For API endpoints, use this format:

```mdx
---
title: 'Endpoint Name'
api: 'METHOD /path'
description: 'What this endpoint does'
---

## Request

<ParamField path="param" type="string" required>
  Description
</ParamField>

## Response

<ResponseField name="field" type="string">
  Description
</ResponseField>

<RequestExample>
```bash cURL
curl -X GET "https://api.innova-trading.com/path"
```
</RequestExample>

<ResponseExample>
```json
{
  "success": true
}
```
</ResponseExample>
```

## Resources

- [Mintlify Documentation](https://mintlify.com/docs)
- [MDX Syntax](https://mdxjs.com/)
- [Mintlify Components](https://mintlify.com/docs/components)
