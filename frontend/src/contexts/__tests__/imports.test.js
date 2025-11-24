import { describe, it, expect } from 'vitest'
import { AuthProvider } from '../AuthContext'

describe('Context Imports', () => {
  it('AuthProvider deve existir', () => {
    expect(AuthProvider).toBeDefined()
  })

  it('AuthProvider deve ser uma função', () => {
    expect(typeof AuthProvider).toBe('function')
  })
})
