import { describe, it, expect } from 'vitest'
import Navbar from '../Navbar'
import PrivateRoute from '../PrivateRoute'
import PublicNavbar from '../PublicNavbar'

describe('Component Imports', () => {
  it('Navbar deve existir', () => {
    expect(Navbar).toBeDefined()
  })
  
  it('Navbar deve ser um componente', () => {
    expect(typeof Navbar).toBe('function')
  })

  it('PrivateRoute deve existir', () => {
    expect(PrivateRoute).toBeDefined()
  })
  
  it('PrivateRoute deve ser um componente', () => {
    expect(typeof PrivateRoute).toBe('function')
  })

  it('PublicNavbar deve existir', () => {
    expect(PublicNavbar).toBeDefined()
  })
  
  it('PublicNavbar deve ser um componente', () => {
    expect(typeof PublicNavbar).toBe('function')
  })
})
