function toNumber(value) {
  const number = Number(value)
  return Number.isFinite(number) ? number : 0
}

export function formatMoney(value) {
  return `¥${toNumber(value).toFixed(2)}`
}

export function formatPlainMoney(value) {
  return toNumber(value).toFixed(2)
}

export function formatPercent(value) {
  const number = Math.min(Math.max(toNumber(value), 0), 1)
  return `${(number * 100).toFixed(1)}%`
}
