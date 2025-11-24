import { describe, it, expect } from 'vitest'
import api from '../api'

describe('Service Imports', () => {
  it('api deve existir', () => {
    expect(api).toBeDefined()
  })

  it('api deve ter defaults', () => {
    expect(api.defaults).toBeDefined()
  })

  it('api deve ter baseURL', () => {
    expect(api.defaults.baseURL).toBeDefined()
  })

  it('api deve ter interceptors', () => {
    expect(api.interceptors).toBeDefined()
  })

  it('api deve ter request interceptor', () => {
    expect(api.interceptors.request).toBeDefined()
  })

  it('api deve ter response interceptor', () => {
    expect(api.interceptors.response).toBeDefined()
  })

  it('api deve ter método get', () => {
    expect(api.get).toBeDefined()
    expect(typeof api.get).toBe('function')
  })

  it('api deve ter método post', () => {
    expect(api.post).toBeDefined()
    expect(typeof api.post).toBe('function')
  })

  it('api deve ter método put', () => {
    expect(api.put).toBeDefined()
    expect(typeof api.put).toBe('function')
  })

  it('api deve ter método delete', () => {
    expect(api.delete).toBeDefined()
    expect(typeof api.delete).toBe('function')
  })
})
