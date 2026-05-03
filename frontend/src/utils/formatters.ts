/**
 * Format a date string (e.g., "2023-01-01T12:00:00Z") to "YYYY/MM/DD"
 */
export const formatDate = (dateStr: string | undefined | null): string => {
  if (!dateStr) return '-'
  return dateStr.split('T')[0].replace(/-/g, '/')
}
