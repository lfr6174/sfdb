# 臺灣科幻概念資料庫 (Taiwan sf Database) Frontend

This is a modern Vue 3 + TypeScript + Vite project for the Taiwan sf Database frontend. It utilizes `<script setup>` syntax and Tailwind CSS to ensure a readable, modular, and highly maintainable codebase.

## Project Structure & Architecture

The project follows clear separation of concerns to allow developers of all levels to easily locate and update code:

```text
src/
├── api/             # Axios configuration and backend API wrappers
├── components/      # Reusable UI components (e.g., Navbar, PaginationControls)
├── composables/     # Shared stateful logic (e.g., useSpoiler)
├── utils/           # Stateless utility functions (e.g., formatters)
├── views/           # Page-level components corresponding to vue-router views
├── App.vue          # Main application entry point
├── main.ts          # Vue application bootstrapping
└── style.css        # Global styles and Tailwind semantic variable configurations
```

### Key Design Principles

1. **Modularity without over-engineering**: We extracted only genuinely reused logic.
   - e.g., The "Spoiler toggle" relies on a custom global state hook (`useSpoiler`) instead of hacky Window CustomEvents.
   - e.g., Complex repetitive layouts like `PaginationControls` have been grouped, while unique view details stay in their respective view templates.
2. **Semantic Styling**: Please avoid hardcoding hex values in component tags. CSS variables (such as `bg-bg`, `text-main`, `text-primary`) are established in `style.css`.
3. **Explicit Logic**: We prefer standard readable `try/catch/finally` blocks and clear Vue `refs` over obscure reactive proxy magic.

### Styling Guide (`style.css`)

To ensure consistent design and avoid massive blocks of repeated Tailwind utility classes in templates, we maintain reusable component classes in `src/style.css` using Tailwind's `@layer components` directive.

**When building or updating `.vue` views, apply these classes instead of hardcoding:**

- **Containers**: `.card`, `.card-sm` (For white panels with rounded corners and subtle borders).
- **Typography**: `.section-label` (For uppercase, tracking-wide subheadings), `.flat-title`, `.flat-sub`.
- **Interactive Elements**: `.btn-primary` (Solid buttons), `.btn-outline` (Outlined buttons).
- **Forms**: `.form-input` (Standard text inputs), `.form-select` (Dropdowns).
- **Tags & Badges**: `.tag` (Clickable label), `.pill` (Smaller label), `.badge` (Non-clickable stat tag).
- **List Items**: `.list-row` (Bordered row with hover effect), `.flat-row` (Compacter row for sidebars), `.concept-row`.
- **Utilities**: `.back-link` (For "← Back" navigational texts), `.spoiler` (For blurred spoiler-protected text).

## How to Maintain and Extend

### Adding a New View

1. Create a `.vue` file in the `src/views/` folder and use `<script setup lang="ts">`.
2. Try to reuse existing tailwind utility components like `.card`, `.tag`, or `.section-label`.
3. Connect to backend data natively using imports from `src/api/axios`.

### Handling Spoilers

Access the global state to read or update whether users are protecting themselves from spoilers:

```ts
import { useSpoiler } from '@/composables/useSpoiler'

const { isSpoilerProtected, revealSpoiler, revealedSpoilers } = useSpoiler()
```

Wrap spoiler-heavy texts and tie clicks to the `revealSpoiler(id)` method.

### Utility Functions

Need to process data before rendering? Utilize or add to the files in `src/utils`. Example:

```ts
import { formatDate } from '@/utils/formatters'
```
