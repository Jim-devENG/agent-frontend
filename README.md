# Frontend Dashboard

Next.js frontend for art outreach automation system.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Set environment variables (create `.env.local` file):
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
```

3. Start development server:
```bash
npm run dev
```

4. Open http://localhost:3000

## Project Structure

```
frontend-new/
├── app/
│   ├── layout.tsx
│   ├── page.tsx             # Dashboard
│   ├── prospects/            # Prospects list page
│   ├── jobs/                 # Jobs list page
│   └── settings/             # Settings page
├── components/
│   ├── ProspectTable.tsx
│   ├── JobList.tsx
│   ├── EmailComposer.tsx
│   └── ...
├── lib/
│   ├── api.ts               # API client
│   └── types.ts             # TypeScript types
├── public/
└── package.json
```

## Build for Production

```bash
npm run build
```

## Deployment

Deploy to Vercel:
1. Connect GitHub repository
2. Set root directory to `frontend-new/`
3. Configure environment variables
4. Deploy automatically on push

