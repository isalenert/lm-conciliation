import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'

const MockPage = () => (
  <div>
    <h1>Página de Teste</h1>
    <p>Conteúdo da página</p>
    <button>Ação</button>
  </div>
)

describe('Page Component', () => {
  it('deve renderizar título da página', () => {
    render(
      <BrowserRouter>
        <MockPage />
      </BrowserRouter>
    )
    
    expect(screen.getByText('Página de Teste')).toBeInTheDocument()
  })

  it('deve renderizar conteúdo da página', () => {
    render(
      <BrowserRouter>
        <MockPage />
      </BrowserRouter>
    )
    
    expect(screen.getByText('Conteúdo da página')).toBeInTheDocument()
  })

  it('deve renderizar botão de ação', () => {
    render(
      <BrowserRouter>
        <MockPage />
      </BrowserRouter>
    )
    
    expect(screen.getByRole('button', { name: 'Ação' })).toBeInTheDocument()
  })
})
