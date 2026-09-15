const BASE_URL = (import.meta.env?.VITE_API_URL || '').replace(/\/$/, '')

async function request(method, path, body) {
  let res
  try {
    res = await fetch(`${BASE_URL}${path}`, {
      method,
      headers: body === undefined ? {} : { 'Content-Type': 'application/json' },
      body: body === undefined ? undefined : JSON.stringify(body),
      signal: AbortSignal.timeout(30_000),
    })
  } catch (error) {
    throw new Error(error.name === 'TimeoutError'
      ? 'The demo service took too long to respond. Please try again.'
      : 'Cannot reach the demo service. Check your connection and try again.')
  }

  const data = await res.json().catch(() => null)
  if (!res.ok) {
    throw new Error(typeof data?.detail === 'string'
      ? data.detail
      : `The demo service could not complete this request (${res.status}). Please try again.`)
  }
  if (!data) throw new Error('The demo service returned an unreadable response. Please try again.')
  return data
}

export const api = {
  query: (question) => request('POST', '/query', { question }),
  getDemo: () => request('GET', '/demo'),
}
