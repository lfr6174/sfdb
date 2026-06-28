// Vercel Edge Function: server-renders the OG/meta tags for detail pages so
// social crawlers (and search engines) see per-page title/description.
// Real users still get a fully working SPA shell — only <head> differs.
//
// Routing: vercel.json rewrites /works/:id (etc.) to /api/render?type=work&key=:id

export const config = { runtime: 'edge' }

// Maps a frontend route type to its API collection path and the API fields
// that supply the social title / description.
const TYPE_MAP: Record<
  string,
  { path: string; titleField: string; descField: string }
> = {
  work: { path: 'works', titleField: 'title', descField: 'description' },
  concept: { path: 'concepts', titleField: 'name', descField: 'description' },
  person: { path: 'persons', titleField: 'name', descField: 'about' },
  post: { path: 'posts', titleField: 'title', descField: 'body' },
  page: { path: 'pages', titleField: 'title', descField: 'body' },
}

const SITE_NAME = '臺灣科幻概念資料庫'

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function truncate(value: string, max = 160): string {
  const clean = value.replace(/\s+/g, ' ').trim()
  return clean.length > max ? `${clean.slice(0, max - 1)}…` : clean
}

export default async function handler(req: Request): Promise<Response> {
  const url = new URL(req.url)
  const type = url.searchParams.get('type') ?? ''
  const key = url.searchParams.get('key') ?? ''
  const config = TYPE_MAP[type]

  // Always fetch the built SPA shell as the template (real static file).
  const shell = await fetch(`${url.origin}/index.html`)
  let html = await shell.text()

  const apiBase = (process.env.API_BASE_URL ?? '').replace(/\/$/, '')

  // If we can't resolve the route or the API, just return the default shell.
  if (config && key && apiBase) {
    try {
      const res = await fetch(`${apiBase}/${config.path}/${encodeURIComponent(key)}/`, {
        headers: { Accept: 'application/json' },
      })
      if (res.ok) {
        const data = (await res.json()) as Record<string, unknown>
        const rawTitle = String(data[config.titleField] ?? '').trim()
        const rawDesc = String(data[config.descField] ?? '').trim()

        if (rawTitle) {
          const pageTitle = `${rawTitle} | ${SITE_NAME}`
          const desc = truncate(rawDesc || `${rawTitle}－${SITE_NAME}`)
          const canonical = `${url.origin}${url.pathname}`

          const t = escapeHtml(pageTitle)
          const d = escapeHtml(desc)
          const og = [
            `<meta name="description" content="${d}" />`,
            `<meta property="og:type" content="article" />`,
            `<meta property="og:site_name" content="${escapeHtml(SITE_NAME)}" />`,
            `<meta property="og:title" content="${t}" />`,
            `<meta property="og:description" content="${d}" />`,
            `<meta property="og:url" content="${escapeHtml(canonical)}" />`,
            `<meta name="twitter:card" content="summary" />`,
            `<meta name="twitter:title" content="${t}" />`,
            `<meta name="twitter:description" content="${d}" />`,
            `<link rel="canonical" href="${escapeHtml(canonical)}" />`,
          ].join('\n    ')

          html = html
            .replace(/<title>[\s\S]*?<\/title>/, `<title>${t}</title>`)
            .replace(/<!-- OG_META -->[\s\S]*?<!-- \/OG_META -->/, og)
        }
      }
    } catch {
      // Network/API failure → fall through to the default shell.
    }
  }

  return new Response(html, {
    headers: {
      'Content-Type': 'text/html; charset=utf-8',
      // Edge-cache the rendered shell; serve stale while revalidating.
      'Cache-Control': 's-maxage=3600, stale-while-revalidate=86400',
    },
  })
}
