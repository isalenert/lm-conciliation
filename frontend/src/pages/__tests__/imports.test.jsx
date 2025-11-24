import { describe, it, expect } from 'vitest'
import Home from '../Home'
import Login from '../Login'
import SignUp from '../SignUp'
import Dashboard from '../Dashboard'
import Upload from '../Upload'
import History from '../History'
import Settings from '../Settings'
import ForgotPassword from '../ForgotPassword'
import ResetPassword from '../ResetPassword'

describe('Page Imports', () => {
  it('Home deve existir', () => {
    expect(Home).toBeDefined()
  })

  it('Login deve existir', () => {
    expect(Login).toBeDefined()
  })

  it('SignUp deve existir', () => {
    expect(SignUp).toBeDefined()
  })

  it('Dashboard deve existir', () => {
    expect(Dashboard).toBeDefined()
  })

  it('Upload deve existir', () => {
    expect(Upload).toBeDefined()
  })

  it('History deve existir', () => {
    expect(History).toBeDefined()
  })

  it('Settings deve existir', () => {
    expect(Settings).toBeDefined()
  })

  it('ForgotPassword deve existir', () => {
    expect(ForgotPassword).toBeDefined()
  })

  it('ResetPassword deve existir', () => {
    expect(ResetPassword).toBeDefined()
  })
})
