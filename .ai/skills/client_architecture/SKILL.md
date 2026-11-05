

# Next.js Architecture Skill

## 1. Purpose

Follow these standards whenever creating, modifying, reviewing, or organizing a Next.js project for Krishna.

Priorities:

1. Performance from the beginning.
2. React Server Components by default.
3. Minimal client-side JavaScript and hydration.
4. Small, reusable components and modules.
5. Consistent folder structure and naming.
6. Strong TypeScript typing.
7. Secure server-side operations.
8. Maintainable code with no oversized files.

Follow explicit project-specific instructions when they override these defaults.

## 2. Standard Technology Stack

- Next.js App Router
- TypeScript and TSX
- React Server Components
- TanStack React Query for client-side server state
- Axios for HTTP requests
- Zustand for client-side global state
- Firebase when required
- Tailwind CSS when configured
- Zod for runtime validation when appropriate

Do not introduce unnecessary dependencies.

## 3. Standard Folder Structure

```text
project/
├── public/
│   ├── images/
│   ├── icons/
│   └── fonts/
│
├── src/
│   ├── app/
│   │   ├── auth/
│   │   │   ├── _partials/
│   │   │   │   ├── LoginForm.tsx
│   │   │   │   ├── LoginHeader.tsx
│   │   │   │   ├── imports/
│   │   │   │   │   └── useLoginMutation.ts
│   │   │   │   └── actions/
│   │   │   │       └── login.ts
│   │   │   ├── page.tsx
│   │   │   └── layout.tsx
│   │   │
│   │   ├── domain/
│   │   │   ├── _partials/
│   │   │   │   ├── DomainTable.tsx
│   │   │   │   ├── DomainRow.tsx
│   │   │   │   ├── DomainFilters.tsx
│   │   │   │   ├── imports/
│   │   │   │   │   └── useGetDomainsQuery.ts
│   │   │   │   └── actions/
│   │   │   │       ├── createDomain.ts
│   │   │   │       ├── updateDomain.ts
│   │   │   │       └── deleteDomain.ts
│   │   │   ├── page.tsx
│   │   │   └── layout.tsx
│   │   │
│   │   ├── users/
│   │   │   ├── _partials/
│   │   │   │   ├── UserTable.tsx
│   │   │   │   ├── UserForm.tsx
│   │   │   │   ├── imports/
│   │   │   │   └── actions/
│   │   │   ├── page.tsx
│   │   │   └── layout.tsx
│   │   │
│   │   ├── api/
│   │   │   └── health/
│   │   │       └── route.ts
│   │   │
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── globals.css
│   │   ├── loading.tsx
│   │   ├── error.tsx
│   │   └── not-found.tsx
│   │
│   ├── components/
│   │   ├── shared/
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Modal.tsx
│   │   │   └── DataTable.tsx
│   │   └── layout/
│   │       ├── Sidebar.tsx
│   │       ├── Navbar.tsx
│   │       └── AppShell.tsx
│   │
│   ├── lib/
│   │   ├── axios.ts
│   │   ├── query-client.ts
│   │   ├── firebase.ts
│   │   ├── utils.ts
│   │   ├── providers/
│   │   │   └── QueryClientProvider.tsx
│   │   └── store/
│   │       ├── useAuth.ts
│   │       ├── useUI.ts
│   │       └── useSomething.ts
│   │
│   ├── @types/
│   │   ├── index.d.ts
│   │   ├── api.d.ts
│   │   ├── user.d.ts
│   │   ├── domain.d.ts
│   │   └── auth.d.ts
│   │
│   ├── hooks/
│   │   └── useDebounce.ts
│   │
│   ├── constants/
│   │   └── index.ts
│   │
│   └── utils/
│       └── format-date.ts
│
├── .ai/
│   └── skills/
│       └── nextjs-architecture/
│           └── SKILL.md
│
├── .env.example
├── .gitignore
├── eslint.config.mjs
├── next.config.ts
├── tsconfig.json
├── package.json
└── README.md
```

This structure is a baseline. Create files and directories only when needed.

## 4. Route Organization

### `app/`

Use the Next.js App Router for routes, layouts, loading states, errors, and HTTP route handlers.

- `page.tsx`: compose the page.
- `layout.tsx`: persistent layout for a route segment.
- `loading.tsx`: loading UI.
- `error.tsx`: error boundary; must be a Client Component.
- `not-found.tsx`: not-found UI.
- `api/**/route.ts`: HTTP endpoints when needed.

Keep page files focused. Avoid implementing an entire page inside one large component.

### `app/**/_partials/`

Store components used exclusively by a route or route segment.

Examples:

- `UserTable.tsx`
- `UserRow.tsx`
- `UserFilters.tsx`
- `UserForm.tsx`
- `UserEmptyState.tsx`

Split components according to responsibility. Move genuinely reusable UI into `components/shared/` or `components/layout/`.

Next.js private folders prefixed with `_` do not create routes.

### `app/**/_partials/imports/`

Store route-specific React Query hooks here.

Examples:

- `useGetUsersQuery.ts`
- `useGetUserQuery.ts`
- `useCreateUserMutation.ts`
- `useUserUpdateMutation.ts`
- `useDeleteUserMutation.ts`

Use Axios through the shared client in `lib/axios.ts`.

If a hook becomes genuinely reusable across routes, move it to a shared location such as `lib/queries/`. Do not duplicate hooks unnecessarily.

### `app/**/_partials/actions/`

Store route-specific Server Actions here.

Examples:

- `createUser.ts`
- `updateUser.ts`
- `deleteUser.ts`

Rules:

- Use `'use server'` at the top of dedicated Server Action modules.
- Validate every input on the server.
- Authenticate and authorize every operation.
- Never trust client-provided permissions, roles, ownership, or prices.
- Keep privileged database access and secrets on the server.
- Return serializable results.
- Revalidate affected paths or tags when appropriate.
- Keep ordinary helper functions in separate modules.
- Use Route Handlers instead when an actual HTTP endpoint is required.

Server Actions are externally invocable entry points. Their folder location does not make them private or secure automatically.

## 5. Global TypeScript Types and Interfaces

**All shared types and interfaces must be stored in `src/@types/`.**

Do not create a separate `src/types/` directory.

Organize global definitions by domain:

```text
src/@types/
├── index.d.ts
├── api.d.ts
├── auth.d.ts
├── user.d.ts
├── domain.d.ts
├── campaign.d.ts
└── common.d.ts
```

Create only the files required by the project.

### Type organization rules

- `api.d.ts`: shared API response, pagination, and error structures.
- `auth.d.ts`: shared authentication and session-related types.
- `user.d.ts`: shared user entity and user-related types.
- `domain.d.ts`: shared domain entity and domain-related types.
- `campaign.d.ts`: shared campaign entity and campaign-related types.
- `common.d.ts`: genuinely generic types shared across multiple features.
- `index.d.ts`: shared ambient declarations or carefully selected type exports when appropriate.

Do not turn `index.d.ts` into a giant dumping ground.

### Example: `src/@types/api.d.ts`

```ts
/**
 * @author Krishna
 * @license MIT
 */

export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface ApiError {
  message: string;
  statusCode?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  page: number;
  limit: number;
  total: number;
  totalPages: number;
}
```

### Example: `src/@types/user.d.ts`

```ts
/**
 * @author Krishna
 * @license MIT
 */

export interface User {
  id: string;
  name: string;
  email: string;
  createdAt: string;
  updatedAt: string;
}

export interface CreateUserInput {
  name: string;
  email: string;
}

export interface UpdateUserInput {
  name?: string;
  email?: string;
}
```

### Global types versus local implementation details

Store shared domain types and interfaces in `src/@types/`.

Keep implementation-specific details local when they are not part of the shared application contract. For example, a private component's internal props type can remain beside that component if it is not reused elsewhere.

Do not force every small local type into a global file.

Use imports such as:

```ts
import type { User, UpdateUserInput } from "@types/user";
```

Configure the alias in `tsconfig.json` if using `@types/*` imports. Avoid relying on implicit alias behavior.

Example path configuration:

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@types/*": ["src/@types/*"]
    }
  }
}
```

Keep `tsconfig.json` valid JSON. Never insert comments into JSON files.

Use `.d.ts` for declaration files and ambient declarations. For ordinary exported application types, `.ts` files are also valid if that better fits the project's type-module conventions. Keep the required directory consistent.

## 6. Server Components by Default

Server Components are the default. Do not add `'use client'` unless a component requires:

- React state or effects.
- Event handlers.
- Browser APIs.
- Zustand hooks.
- React Query hooks.
- Client-only third-party libraries.

Place the client boundary as low as possible in the component tree.

Prefer Server Components for:

- Initial page rendering.
- Server-side data access.
- Static content.
- Non-interactive tables and summaries.
- Page composition.

Use Client Components for:

- Interactive forms and controls.
- Dialogs and dropdowns that need client state.
- React Query hooks.
- Zustand store consumers.
- Browser-only functionality.

Do not mark an entire page or layout as a Client Component just because one child needs interactivity.

Pass serializable props across Server/Client boundaries.

## 7. React Query and Axios

React Query owns client-side server state, including caching, refetching, mutations, and optimistic updates.

Axios provides centralized HTTP configuration.

### Axios

Keep the shared Axios instance in `src/lib/axios.ts`.

Centralize:

- Base URL.
- Request timeout.
- Shared headers.
- Safe interceptors.
- Consistent error handling where appropriate.

Never put secrets in `NEXT_PUBLIC_*` environment variables.

### React Query

Keep route-specific hooks inside `_partials/imports/`.

- Use stable query keys, such as `['users', userId]`.
- Include changing inputs in query keys.
- Use `enabled` when a valid input is required.
- Configure stale time and retries intentionally.
- Update or invalidate the correct query keys after mutations.
- Avoid duplicate requests and unnecessary refetches.
- Avoid retrying non-recoverable errors without reason.
- Use a per-browser QueryClient instance.
- Never share a mutable QueryClient singleton across server requests.

Use Server Components for initial data when server rendering is more appropriate. Use React Query when client-side caching, refetching, mutations, optimistic updates, or synchronization provide value.

Do not force every request through client-side React Query.

## 8. Zustand Stores

All Zustand stores belong in `src/lib/store/`.

Examples:

- `useAuth.ts`
- `useUI.ts`
- `useSidebar.ts`
- `usePreferences.ts`

Use Zustand for client-owned global state, such as UI preferences, active selections, and state shared between distant client components.

Do not duplicate React Query responses in Zustand.

React Query owns server state. Zustand owns client state.

A Zustand authentication flag is not authorization. Enforce identity and permissions on the server using secure authentication and session mechanisms.

## 9. Global Components

### `components/shared/`

Store globally reusable UI:

- Buttons.
- Inputs.
- Dialogs.
- Badges.
- Tables.
- Pagination controls.
- Reusable loading and empty states.

### `components/layout/`

Store shared structural UI:

- Sidebar.
- Navbar.
- Header.
- Footer.
- App shell.

Avoid putting route-specific business logic into global UI components.

## 10. File Header Requirement

Every source file must begin with this comment, adjusted to the comment syntax supported by the file type:

```tsx
/**
 * @author Krishna
 * @license MIT
 */
```

Apply the header to TypeScript, TSX, JavaScript, CSS, and other source files that support comments.

JSON does not support comments. Never make JSON invalid to satisfy the header rule. Document this exception in the project conventions.

Choose one project license, such as `MIT` or `Apache-2.0`. Do not write "Apache 2.0 or MIT" as if they were interchangeable. Ensure the repository's LICENSE file matches the selected license.

## 11. Strict File Size Limit

Every source and configuration file must remain **under 200 lines** where practical and where the format permits comments.

Treat 199 lines as the maximum.

Count:

- The header.
- Imports.
- Blank lines.
- Types.
- Implementation.
- Exports.

Rules:

- Split large components into cohesive subcomponents.
- Extract schemas, types, actions, and utilities when they grow.
- Keep each module focused on one responsibility.
- Do not split code into meaningless files just to satisfy the limit.
- Do not generate unnecessary placeholder files.
- Refactor before a file reaches 200 lines.

JSON files must remain valid and should also stay under the limit.

## 12. Performance Standards

Optimize from the beginning without sacrificing correctness.

1. Prefer Server Components and minimize client JavaScript.
2. Put `'use client'` on the smallest useful interactive boundary.
3. Avoid unnecessary global providers.
4. Fetch independent server-side data concurrently where appropriate.
5. Use Next.js caching and revalidation deliberately.
6. Avoid request waterfalls and duplicate requests.
7. Use dynamic imports only when deferring genuinely heavy or non-critical code is beneficial.
8. Use stable React keys.
9. Avoid unnecessary effects and duplicated state.
10. Paginate or virtualize large datasets when appropriate.
11. Avoid giant barrel files and unnecessarily broad imports.
12. Optimize images with `next/image` where appropriate.
13. Prevent database N+1 queries and fetch only required fields.
14. Avoid expensive synchronous work during rendering.
15. Use production builds, bundle analysis, and Core Web Vitals to validate performance.

Do not claim a performance improvement without evidence.

## 13. Security and Quality

- Enable strict TypeScript settings.
- Validate untrusted data at server boundaries.
- Authenticate and authorize every Server Action.
- Keep secrets and privileged operations server-only.
- Never rely on client-side role checks for authorization.
- Handle loading, error, empty, and success states.
- Avoid `any` unless justified.
- Keep shared types consistent across API hooks and components.
- Use runtime validation for untrusted API inputs and action payloads where appropriate.
- Avoid unnecessary dependencies and abstractions.
- Keep modules cohesive and easy to test.

## 14. Completion Checklist

Before completing a task, verify:

- [ ] Route-specific UI is inside `app/**/_partials/`.
- [ ] Route-specific React Query hooks are inside `_partials/imports/`.
- [ ] Route-specific Server Actions are inside `_partials/actions/`.
- [ ] Shared types and interfaces are inside `src/@types/`.
- [ ] No separate `src/types/` directory is introduced.
- [ ] Global UI is inside `components/shared/` or `components/layout/`.
- [ ] Zustand stores are inside `lib/store/`.
- [ ] Axios and Query Client configuration are centralized in `lib/`.
- [ ] Server Components are used by default.
- [ ] Client Components exist only where necessary.
- [ ] Server Actions validate input and enforce authorization.
- [ ] Every applicable source file has the author/license header.
- [ ] No file reaches 200 lines.
- [ ] React Query server state is not duplicated in Zustand.
- [ ] Secrets remain server-only.
- [ ] Caching and revalidation are deliberate.
- [ ] Type checks, linting, and production builds pass when the environment permits.
