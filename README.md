# RepoMind

> AI-powered codebase analysis and repository intelligence platform for developers

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](frontend/package.json)
[![Built for ETHOnline 2025](https://img.shields.io/badge/Built%20for-ETHOnline%202025-blueviolet.svg)](https://ethglobal.com/)

## Overview

RepoMind is an intelligent platform that helps developers understand, analyze, and interact with their codebases through AI-powered conversations. It provides deep repository insights, code comprehension, and contextual answers by indexing your repositories and leveraging advanced language models.

## Key Features

- **🤖 AI-Powered Code Chat** - Conversational interface for querying and understanding your codebase
- **📦 Multi-Repository Support** - Analyze and chat with multiple repositories simultaneously
- **🔍 Intelligent Code Search** - Semantic search across your entire codebase with context-aware results
- **📊 Repository Analytics** - Complexity scoring, language distribution, and codebase insights
- **🎯 Source Code Citations** - AI responses include direct references to relevant code sections
- **🌿 Branch Management** - Switch and analyze different branches of your repositories
- **⭐ Favorites & Organization** - Star and organize your most important repositories
- **🎨 Modern UI/UX** - Clean, responsive interface with dark mode support

## Architecture

RepoMind follows a modular monorepo architecture:

```
repomind-ui/
├── frontend/              # Next.js frontend application
│   ├── src/
│   │   ├── app/          # Next.js 14 App Router pages
│   │   │   ├── chat/     # Main chat interface
│   │   │   ├── dashboard/# Repository dashboard
│   │   │   └── login/    # Authentication
│   │   ├── components/   # React components
│   │   │   ├── ai/       # AI chat components
│   │   │   ├── ui/       # shadcn/ui components
│   │   │   └── layout/   # Layout components
│   │   ├── hooks/        # Custom React hooks
│   │   ├── lib/          # Utility libraries
│   │   └── types/        # TypeScript type definitions
│   └── public/           # Static assets
```

### Technology Stack

| Layer                     | Technology                              |
| ------------------------- | --------------------------------------- |
| **Frontend Framework**    | Next.js 14 (App Router)                 |
| **Language**              | TypeScript                              |
| **Styling**               | Tailwind CSS                            |
| **UI Components**         | shadcn/ui + Radix UI                    |
| **State Management**      | React Hooks                             |
| **AI Integration**        | Vercel AI SDK                           |
| **Markdown Rendering**    | react-markdown + remark-gfm             |
| **Animations**            | Framer Motion                           |
| **Package Manager**       | pnpm 9.12.0                             |

## Quick Start

### Prerequisites

- **Node.js** 18.14+ or 20.x
- **pnpm** 9.12.0+
- **Git**

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/repomind-ui.git
cd repomind-ui
```

2. **Install dependencies**
```bash
# Install pnpm if you don't have it
npm install -g pnpm@9.12.0

# Install project dependencies
cd frontend
pnpm install
```

3. **Set up environment variables**
```bash
# Create .env.local in frontend directory
cp .env.example .env.local

# Edit .env.local with your configuration
# Required variables:
# - NEXT_PUBLIC_API_URL=http://localhost:4000
# - OPENAI_API_KEY=your_openai_key
```

4. **Run the development server**
```bash
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) to see the application.

## Development

### Available Commands

```bash
# Frontend development
cd frontend

pnpm dev          # Start development server (port 3000)
pnpm build        # Build for production
pnpm start        # Start production server
pnpm lint         # Run ESLint
```

## Configuration

### pnpm Workspace

This project uses pnpm workspaces for efficient dependency management. The `packageManager` field in `package.json` ensures everyone uses the same pnpm version:

```json
{
  "packageManager": "pnpm@9.12.0+sha512.4abf725084d7bcbafbd728bfc7bee61f2f791f977fd87542b3579dcb23504d170d46337945e4c66485cd12d588a0c0e570ed9c477e7ccdd8507cf05f3f92eaca"
}
```

### Tailwind Configuration

Custom theme extensions for RepoMind branding and shadcn/ui integration can be found in `frontend/tailwind.config.ts`.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Next.js](https://nextjs.org)
- UI components from [shadcn/ui](https://ui.shadcn.com)
- Icons from [Lucide](https://lucide.dev)
- AI SDK by [Vercel](https://sdk.vercel.ai)

---

Built for **ETHOnline 2025**
