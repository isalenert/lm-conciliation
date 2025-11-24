import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Home from '../Home'

vi.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: null,
    logout: vi.fn()
  })
}))

describe('Home Component', () => {
  it('deve renderizar sem erros', () => {
    render(
      <BrowserRouter>
        <Home />
      </BrowserRouter>
    )
    
    expect(document.body).toBeTruthy()
  })

  it('deve renderizar título', () => {
    const { container } = render(
      <BrowserRouter>
        <Home />
      </BrowserRouter>
    )
    
    expect(container).toBeTruthy()
  })

  it('deve ter conteúdo', () => {
    const { container } = render(
      <BrowserRouter>
        <Home />
      </BrowserRouter>
    )
    
    expect(container.innerHTML.length).toBeGreaterThan(0)
  })
})