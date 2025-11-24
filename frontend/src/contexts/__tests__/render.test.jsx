import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { AuthProvider, useAuth } from '../AuthContext'

describe('AuthContext Render', () => {
  it('AuthProvider renderiza children', () => {
    const TestComponent = () => {
      const { user } = useAuth()
      return <div>Status: {user ? 'logged' : 'not logged'}</div>
    }

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )

    expect(screen.getByText(/Status:/)).toBeInTheDocument()
  })

  it('AuthProvider tem funções', () => {
    const TestComponent = () => {
      const { login, logout } = useAuth()
      return (
        <div>
          <button onClick={() => login({})}>Login</button>
          <button onClick={logout}>Logout</button>
        </div>
      )
    }

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )

    expect(screen.getByText('Login')).toBeInTheDocument()
    expect(screen.getByText('Logout')).toBeInTheDocument()
  })
})
