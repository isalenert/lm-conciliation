import { describe, it, expect, vi } from 'vitest'
import { render } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Navbar from '../Navbar'
import PrivateRoute from '../PrivateRoute'
import PublicNavbar from '../PublicNavbar'

vi.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { email: 'test@test.com' },
    logout: vi.fn()
  })
}))

describe('Render All Components', () => {
  it('Navbar renderiza', () => {
    const { container } = render(<BrowserRouter><Navbar /></BrowserRouter>)
    expect(container.innerHTML.length).toBeGreaterThan(0)
  })

  it('PublicNavbar renderiza', () => {
    const { container } = render(<BrowserRouter><PublicNavbar /></BrowserRouter>)
    expect(container.innerHTML.length).toBeGreaterThan(0)
  })

  it('PrivateRoute renderiza', () => {
    const TestChild = () => <div>Test</div>
    const { container } = render(
      <BrowserRouter>
        <PrivateRoute><TestChild /></PrivateRoute>
      </BrowserRouter>
    )
    expect(container).toBeTruthy()
  })
})
