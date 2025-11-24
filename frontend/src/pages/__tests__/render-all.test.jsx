import { describe, it, expect, vi } from 'vitest'
import { render } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Home from '../Home'
import Login from '../Login'
import SignUp from '../SignUp'
import Dashboard from '../Dashboard'
import Upload from '../Upload'
import History from '../History'
import Settings from '../Settings'
import ForgotPassword from '../ForgotPassword'
import ResetPassword from '../ResetPassword'

// Mock do AuthContext
vi.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: null,
    login: vi.fn(),
    logout: vi.fn()
  })
}))

describe('Render All Pages', () => {
  it('Home renderiza', () => {
    const { container } = render(<BrowserRouter><Home /></BrowserRouter>)
    expect(container.innerHTML.length).toBeGreaterThan(0)
  })

  it('Login renderiza', () => {
    const { container } = render(<BrowserRouter><Login /></BrowserRouter>)
    expect(container.innerHTML.length).toBeGreaterThan(0)
  })

  it('SignUp renderiza', () => {
    const { container } = render(<BrowserRouter><SignUp /></BrowserRouter>)
    expect(container.innerHTML.length).toBeGreaterThan(0)
  })

  it('Dashboard renderiza', () => {
    const { container } = render(<BrowserRouter><Dashboard /></BrowserRouter>)
    expect(container.innerHTML.length).toBeGreaterThan(0)
  })

  it('Upload renderiza', () => {
    const { container } = render(<BrowserRouter><Upload /></BrowserRouter>)
    expect(container.innerHTML.length).toBeGreaterThan(0)
  })

  it('History renderiza', () => {
    const { container } = render(<BrowserRouter><History /></BrowserRouter>)
    expect(container.innerHTML.length).toBeGreaterThan(0)
  })

  it('Settings renderiza', () => {
    const { container } = render(<BrowserRouter><Settings /></BrowserRouter>)
    expect(container.innerHTML.length).toBeGreaterThan(0)
  })

  it('ForgotPassword renderiza', () => {
    const { container } = render(<BrowserRouter><ForgotPassword /></BrowserRouter>)
    expect(container.innerHTML.length).toBeGreaterThan(0)
  })

  it('ResetPassword renderiza', () => {
    const { container } = render(<BrowserRouter><ResetPassword /></BrowserRouter>)
    expect(container.innerHTML.length).toBeGreaterThan(0)
  })
})
