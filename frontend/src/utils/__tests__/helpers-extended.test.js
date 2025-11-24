import { describe, it, expect } from 'vitest'
import { formatDate, formatCurrency, validateEmail } from '../helpers'

describe('Helper Functions Extended', () => {
  describe('formatDate - casos extras', () => {
    it('deve lidar com string de data', () => {
      const result = formatDate('2025-01-15')
      expect(result).toBeTruthy()
    })

    it('deve lidar com undefined', () => {
      const result = formatDate(undefined)
      expect(result).toBe('')
    })

    it('deve lidar com string vazia', () => {
      const result = formatDate('')
      expect(result).toBe('')
    })
  })

  describe('formatCurrency - casos extras', () => {
    it('deve formatar zero', () => {
      const result = formatCurrency(0)
      expect(result).toContain('0')
    })

    it('deve formatar números pequenos', () => {
      const result = formatCurrency(0.01)
      expect(result).toContain('R$')
    })

    it('deve formatar números grandes', () => {
      const result = formatCurrency(1000000)
      expect(result).toContain('R$')
    })

    it('deve lidar com undefined', () => {
      const result = formatCurrency(undefined)
      expect(result).toContain('R$')
    })
  })

  describe('validateEmail - casos extras', () => {
    it('deve validar emails com subdomínio', () => {
      expect(validateEmail('user@mail.example.com')).toBe(true)
    })

    it('deve validar emails com números', () => {
      expect(validateEmail('user123@example.com')).toBe(true)
    })

    it('deve validar emails com hífen', () => {
      expect(validateEmail('user-name@example.com')).toBe(true)
    })

    it('deve rejeitar email sem @', () => {
      expect(validateEmail('userexample.com')).toBe(false)
    })

    it('deve rejeitar email sem domínio', () => {
      expect(validateEmail('user@')).toBe(false)
    })

    it('deve rejeitar apenas espaços', () => {
      expect(validateEmail('   ')).toBe(false)
    })
  })
})
