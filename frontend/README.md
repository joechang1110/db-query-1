# Database Query Tool - Frontend

Frontend application for the Database Query Tool built with React, TypeScript, and Ant Design.

## Setup

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Or with yarn
yarn install
```

### Configuration

Create a `.env.local` file:

```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### Running

```bash
# Development server
npm run dev

# Or with yarn
yarn dev
```

The frontend will be available at http://localhost:5173

### Building

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/  # Reusable React components
│   ├── pages/       # Page components
│   ├── services/    # API client
│   ├── types/       # TypeScript type definitions
│   ├── hooks/       # Custom React hooks
│   ├── styles/      # CSS styles
│   ├── App.tsx      # Main app component
│   └── main.tsx     # Entry point
├── public/          # Static assets
└── package.json     # Dependencies
```

## Features

- Database connection management
- Metadata viewing (tables, views, columns)
- SQL query execution (coming in Phase 4)
- Natural language to SQL (coming in Phase 5)

