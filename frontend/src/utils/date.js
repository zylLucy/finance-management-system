function pad(value) {
  return String(value).padStart(2, '0')
}

export function toYearMonth(value) {
  if (typeof value === 'number') {
    return value
  }

  if (value instanceof Date) {
    return Number(`${value.getFullYear()}${pad(value.getMonth() + 1)}`)
  }

  const text = String(value || '').trim()
  const match = text.match(/^(\d{4})[-/]?(\d{1,2})/)
  if (!match) {
    return 0
  }

  return Number(`${match[1]}${pad(match[2])}`)
}

export function monthLabel(yearMonth) {
  const text = String(yearMonth)
  return `${text.slice(0, 4)}年${text.slice(4, 6)}月`
}

export function currentDateText() {
  const now = new Date()
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`
}

export function currentMonthText() {
  const now = new Date()
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}`
}

export function getMonthDays(yearMonth) {
  const text = String(yearMonth)
  const year = Number(text.slice(0, 4))
  const month = Number(text.slice(4, 6))
  return new Date(year, month, 0).getDate()
}

export function getDayOfMonth(dateText) {
  return Number(String(dateText).slice(8, 10))
}
