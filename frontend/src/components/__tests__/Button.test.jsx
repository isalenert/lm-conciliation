import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'

const Button = ({ children, onClick, disabled = false }) => (
  <button onClick={onClick} disabled={disabled}>
    {children}
  </button>
)

describe('Button Component', () => {
  it('deve renderizar o botão', () => {
    render(<Button>Clique Aqui</Button>)
    expect(screen.getByText('Clique Aqui')).toBeInTheDocument()
  })

  it('deve chamar onClick quando clicado', () => {
    const handleClick = vi.fn()
    render(<Button onClick={handleClick}>Clique</Button>)
    
    const button = screen.getByText('Clique')
    fireEvent.click(button)
    
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('não deve chamar onClick quando desabilitado', () => {
    const handleClick = vi.fn()
    render(<Button onClick={handleClick} disabled>Clique</Button>)
    
    const button = screen.getByText('Clique')
    fireEvent.click(button)
    
    expect(handleClick).not.toHaveBeenCalled()
  })
})
