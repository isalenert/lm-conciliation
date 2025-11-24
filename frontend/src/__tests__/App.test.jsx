import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import App from '../App'

describe('App Component', () => {
  it('deve renderizar sem erros', () => {
    const { container } = render(<App />)
    expect(container).toBeTruthy()
  })

  it('deve ter elemento root', () => {
    const { container } = render(<App />)
    expect(container.firstChild).toBeTruthy()
  })
})
