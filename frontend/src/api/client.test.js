import assert from 'node:assert/strict'
import { test } from 'node:test'
import { api } from './client.js'

test('public requests send no shared secret and preserve actionable errors', async () => {
  const originalFetch = globalThis.fetch
  const calls = []
  try {
    globalThis.fetch = async (url, options) => {
      calls.push({ url, ...options })
      return { ok: true, json: async () => ({ query_id: 'synthetic-check' }) }
    }
    assert.deepEqual(await api.query('A synthetic question?'), { query_id: 'synthetic-check' })
    await api.getDemo()
    assert.deepEqual(calls.map(call => call.url), ['/query', '/demo'])
    assert.equal(calls[0].body, JSON.stringify({ question: 'A synthetic question?' }))
    assert.deepEqual(calls[0].headers, { 'Content-Type': 'application/json' })
    assert.deepEqual(calls[1].headers, {})
    assert.equal(calls[1].body, undefined)
    assert.ok(calls.every(call => call.signal instanceof AbortSignal))

    globalThis.fetch = async () => ({ ok: false, status: 503, json: async () => ({ detail: 'Demo unavailable' }) })
    await assert.rejects(api.getDemo(), /Demo unavailable/)
    globalThis.fetch = async () => ({ ok: false, status: 422, json: async () => ({ detail: [{ msg: 'Invalid question' }] }) })
    await assert.rejects(api.query('x'), /\(422\)/)
    globalThis.fetch = async () => ({ ok: true, json: async () => { throw new SyntaxError() } })
    await assert.rejects(api.getDemo(), /unreadable response/)
    globalThis.fetch = async () => { throw new TypeError('Failed to fetch') }
    await assert.rejects(api.getDemo(), /Cannot reach the demo service/)
    globalThis.fetch = async () => { throw new DOMException('Timed out', 'TimeoutError') }
    await assert.rejects(api.getDemo(), /took too long/)
  } finally {
    globalThis.fetch = originalFetch
  }
})
