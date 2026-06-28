/**
 * Format a date string (e.g., "2023-01-01T12:00:00Z") to "YYYY/MM/DD"
 */
export const formatDate = (dateStr: string | undefined | null): string => {
  if (!dateStr) return '-'
  return dateStr.split('T')[0].replace(/-/g, '/')
}

export function getYearRange(items: { year?: number | string | null }[]): {
  min: number | null
  max: number | null
} {
  const years = items.map((i) => parseInt(String(i.year))).filter((y) => !isNaN(y))
  if (years.length === 0) return { min: null, max: null }
  return { min: Math.min(...years), max: Math.max(...years) }
}
