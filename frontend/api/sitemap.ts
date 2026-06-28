// Vercel Edge Function: builds sitemap.xml dynamically from the backend API,
// so newly added works/concepts/persons/posts appear without a redeploy.
// Routed via vercel.json: /sitemap.xml -> /api/sitemap

export const config = { runtime: 'edge' }

interface Paginated {
  results: Array<Record<string, unknown>>
  next: string | null
}

// Walks DRF pagination, following `next` until exhausted.
async function fetchPaginated(startUrl: string): Promise<Array<Record<string, unknown>>> {
  const items: Array<Record<string, unknown>> = []
  let url: string | null = startUrl
  let guard = 0
  while (url && guard < 200) {
    const res: Response = await fetch(url, { headers: { Accept: 'application/json' } })
    if (!res.ok) break
    const data = (await res.json()) as Paginated
    items.push(...(data.results ?? []))
    url = data.next
    guard += 1
  }
  return items
}

async function fetchArray(apiUrl: string): Promise<Array<Record<string, unknown>>> {
  const res = await fetch(apiUrl, { headers: { Accept: 'application/json' } })
  if (!res.ok) return []
  return (await res.json()) as Array<Record<string, unknown>>
}

function urlEntry(loc: string, lastmod?: string): string {
  const mod = lastmod ? `<lastmod>${lastmod.slice(0, 10)}</lastmod>` : ''
  return `<url><loc>${loc}</loc>${mod}</url>`
}

export default async function handler(req: Request): Promise<Response> {
  const origin = new URL(req.url).origin
  const apiBase = (process.env.API_BASE_URL ?? '').replace(/\/$/, '')

  const staticPaths = ['/', '/concepts', '/persons', '/works', '/posts']
  const entries: string[] = staticPaths.map((p) => urlEntry(`${origin}${p}`))

  if (apiBase) {
    try {
      const [concepts, works, persons, posts, pages] = await Promise.all([
        fetchArray(`${apiBase}/concepts/all/`),
        fetchPaginated(`${apiBase}/works/`),
        fetchPaginated(`${apiBase}/persons/`),
        fetchPaginated(`${apiBase}/posts/`),
        fetchPaginated(`${apiBase}/pages/`),
      ])

      for (const c of concepts) entries.push(urlEntry(`${origin}/concepts/${c.slug}`, c.updated_at as string))
      for (const w of works) entries.push(urlEntry(`${origin}/works/${w.id}`, w.updated_at as string))
      for (const p of persons) entries.push(urlEntry(`${origin}/persons/${p.id}`, p.updated_at as string))
      for (const p of posts) entries.push(urlEntry(`${origin}/posts/${p.id}`, p.created_at as string))
      for (const p of pages) entries.push(urlEntry(`${origin}/pages/${p.slug}`, p.updated_at as string))
    } catch {
      // On API failure, still return the static entries below.
    }
  }

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${entries.join('\n')}
</urlset>`

  return new Response(xml, {
    headers: {
      'Content-Type': 'application/xml; charset=utf-8',
      'Cache-Control': 's-maxage=3600, stale-while-revalidate=86400',
    },
  })
}
