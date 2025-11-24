import { describe, it, expect } from 'vitest'
import { formatDate, formatCurrency, validateEmail } from '../helpers'

describe('Helper Functions', () => {
  describe('formatDate', () => {
     it('deve formatar data corretamente', () => {
       const date = new Date('2025-01-15T12:00:00')
       const formatted = formatDate(date)
       expect(formatted).toMatch(/\d{2}\/01\/2025/)
       expect(formatted).toContain('2025')
})

    it('deve retornar string vazia para data inválida', () => {
      expect(formatDate(null)).toBe('')
    })
  })

  describe('formatCurrency', () => {
    it('deve formatar valor monetário', () => {
      const formatted = formatCurrency(1500.50)
      expect(formatted).toContain('R$')
      expect(formatted).toContain('1')
      expect(formatted).toContain('500')
    })

    it('deve lidar com valores negativos', () => {
      const formatted = formatCurrency(-100)
      expect(formatted).toContain('R$')
      expect(formatted).toContain('100')
    })

    it('deve lidar com valores nulos', () => {
      expect(formatCurrency(null)).toContain('R$')
    })
  })

  describe('validateEmail', () => {
    it('deve validar email correto', () => {
      expect(validateEmail('test@example.com')).toBe(true)
    })

    it('deve rejeitar email inválido', () => {
      expect(validateEmail('invalid')).toBe(false)
      expect(validateEmail('test@')).toBe(false)
      expect(validateEmail('')).toBe(false)
      expect(validateEmail(null)).toBe(false)
    })
  })
})
