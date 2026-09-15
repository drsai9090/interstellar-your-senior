import { useEffect, useRef, useState } from 'react'
import { api } from '../api/client'
import ChatMessage from '../components/ChatMessage'

export default function Chat() {
  const [demo, setDemo] = useState(null)
  const [demoError, setDemoError] = useState('')
  const [input, setInput] = useState('')
  const [answer, setAnswer] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const answerHeading = useRef(null)

  async function loadDemo() {
    setDemoError('')
    try { setDemo(await api.getDemo()) }
    catch (err) { setDemoError(err.message) }
  }

  useEffect(() => { loadDemo() }, [])
  useEffect(() => {
    if (answer) answerHeading.current?.focus()
  }, [answer])

  async function ask(text = input) {
    const question = text.trim()
    if (!question || loading || !demo) return
    setInput(question)
    setError('')
    setAnswer(null)
    setLoading(true)
    try { setAnswer(await api.query(question)) }
    catch (err) { setError(err.message) }
    finally { setLoading(false) }
  }

  return (
    <div className="demo-shell">
      <a className="skip-link" href="#question-input">Skip to question</a>
      <header className="masthead">
        <a className="brand" href="/" aria-label="Interstellar home">
          <svg className="brand-mark" viewBox="0 0 40 40" aria-hidden="true">
            <ellipse cx="20" cy="20" rx="17" ry="7" transform="rotate(-38 20 20)" />
            <circle cx="20" cy="20" r="5" /><circle className="orbit-dot" cx="32" cy="10" r="2.5" />
          </svg>
          <span>INTERSTELLAR<small>Your Senior · Document assistant</small></span>
        </a>
        <a className="repository-link" href="https://github.com/drsai9090/interstellar-your-senior">View project <span aria-hidden="true">↗</span></a>
      </header>

      <main>
        <section className="intro" aria-labelledby="page-title">
          <div>
            <h1 id="page-title">Document search</h1>
            <p className="intro-copy">Ask a sample question and read the source.</p>
          </div>
          <div className="demo-note">
            <span className="demo-tag"><span aria-hidden="true" />Synthetic demo</span>
            <p>Fictional documents and prewritten answers. No live model. Other questions return unsupported.</p>
          </div>
        </section>

        <div className="workspace">
          <section className="question-workspace" aria-labelledby="workspace-heading">
            <div className="section-heading">
              <h2 id="workspace-heading">Question</h2>
            </div>
            <form className="question-form" onSubmit={event => { event.preventDefault(); ask() }}>
              <label htmlFor="question-input">Your question</label>
              <textarea id="question-input" value={input} onChange={event => setInput(event.target.value)}
                onKeyDown={event => {
                  if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
                    event.preventDefault()
                    ask()
                  }
                }}
                placeholder="Ask about the sample documents" rows={2} maxLength={2000}
                aria-describedby="question-help" required disabled={loading} />
              <div className="form-actions">
                <p id="question-help">Ctrl / ⌘ + Enter to ask</p>
                <button className="primary-button" type="submit" disabled={!input.trim() || loading || !demo}>
                  {loading ? 'Checking documents…' : 'Ask question'} <span aria-hidden="true">↗</span>
                </button>
              </div>
            </form>

            {demo && (
              <div className="sample-questions">
                <p className="small-label">Sample questions</p>
                <div className="suggestion-grid">
                  {demo.questions.map(question => (
                    <button type="button" key={question} disabled={loading} onClick={() => ask(question)}>
                      <span>{question}</span><span aria-hidden="true">↗</span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            <p className="request-status" role="status">{loading ? 'Checking sources…' : ''}</p>
            {error && <div className="error-message" role="alert"><strong>Question not completed</strong><p>{error}</p><button type="button" className="text-button" onClick={() => ask()}>Try question again</button></div>}
            {answer && <ChatMessage message={answer} headingRef={answerHeading} />}
          </section>

          <aside className="corpus-panel" aria-labelledby="corpus-heading">
            <div className="section-heading"><h2 id="corpus-heading">Sample documents</h2>{demo && <span className="document-count">{demo.documents.length} docs</span>}</div>
            {demoError ? (
              <div className="error-message" role="alert"><strong>Collection unavailable</strong><p>{demoError}</p><button className="text-button" type="button" onClick={loadDemo}>Retry loading collection</button></div>
            ) : !demo ? <p className="corpus-copy" role="status">Loading sample documents…</p> : (
              <>
                <div className="corpus-documents">
                  {demo.documents.map(document => (
                    <details className="corpus-document" key={document.filename}>
                      <summary aria-label={`Read ${document.filename}`}><span className="document-icon" aria-hidden="true">≡</span><span>{document.filename}</span></summary>
                      <div className="corpus-document-content">{document.content}</div>
                    </details>
                  ))}
                </div>
                <p className="provenance">{demo.description}</p>
              </>
            )}
          </aside>
        </div>
      </main>

      <footer className="footer"><span>Interstellar · Personal prototype</span><span>Built on <a href="https://github.com/Saisugun9090/YOUR-SENIOR-">Your Senior</a></span></footer>
    </div>
  )
}
