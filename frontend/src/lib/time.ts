/**
 * Format a date/timestamp string to Eastern Time.
 */
export function formatTime(dateStr: string | Date): string {
  try {
    const date = new Date(dateStr)
    return date.toLocaleString('en-US', {
      timeZone: 'America/New_York',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    })
  } catch {
    return String(dateStr)
  }
}

export function formatTimeShort(dateStr: string | Date): string {
  try {
    const date = new Date(dateStr)
    return date.toLocaleString('en-US', {
      timeZone: 'America/New_York',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    })
  } catch {
    return String(dateStr)
  }
}
