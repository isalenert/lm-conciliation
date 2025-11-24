import { describe, it, expect, vi } from 'vitest'
import { render } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Navbar from '../Navbar'

vi.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { email: 'test@test.com' },
    logout: vi.fn()
  })
}))

describe('Navbar Component', () => {
  it('deve renderizar sem erros', () => {
    const { container } = render(
      <BrowserRouter>
        <Navbar />
      </BrowserRouter>
    )
    
    expect(container).toBeTruthy()
  })

  it('deve ter navegação', () => {
    const { container } = render(
      <BrowserRouter>
        <Navbar />
      </BrowserRouter>
    )
    
    expect(container.querySelector('nav')).toBeTruthy()
  })

  it('deve ter conteúdo', () => {
    const { container } = render(
      <BrowserRouter>
        <Navbar />
      </BrowserRouter>
    )
    
    expect(container.innerHTML.length).toBeGreaterThan(0)
  })
})
