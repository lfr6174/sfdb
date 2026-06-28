// Vercel Edge Function: serves robots.txt with an absolute Sitemap URL derived
// from the request host (no hardcoded domain). Routed via vercel.json.

export const config = { runtime: 'edge' }

export default function handler(req: Request): Response {
  const origin = new URL(req.url).origin
  const body = `User-agent: *
Allow: /

Sitemap: ${origin}/sitemap.xml
`
  return new Response(body, {
    headers: {
      'Content-Type': 'text/plain; charset=utf-8',
      'Cache-Control': 's-maxage=86400, stale-while-revalidate=604800',
    },
  })
}
