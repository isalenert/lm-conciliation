export const formatDate = (date) => {
  if (!date) return ''
  try {
    const d = new Date(date)
    return d.toLocaleDateString('pt-BR')
  } catch {
    return ''
  }
}

export const formatCurrency = (value) => {
  if (value === null || value === undefined) return 'R$ 0,00'
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value)
}

export const validateEmail = (email) => {
  if (!email) return false
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return regex.test(email)
}
