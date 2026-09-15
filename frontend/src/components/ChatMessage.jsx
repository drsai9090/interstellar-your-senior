import SourceCard from './SourceCard'

const STATUS_LABELS = {
  supported: 'Supported by sample documents',
  partial: 'Partially supported',
  unsupported: 'Unsupported',
}

export default function ChatMessage({ message, headingRef }) {
  return (
    <article className={`answer-card answer-${message.status}`} aria-labelledby="answer-heading">
      <div className="answer-topline">
        <span className={`support-badge support-${message.status}`}>
          <span aria-hidden="true">{message.status === 'supported' ? '✓' : '!'}</span>
          {STATUS_LABELS[message.status] || 'Support status unavailable'}
        </span>
        <span className="answer-mode">{message.response_mode === 'fixture' ? 'Author-written fixture' : message.response_mode === 'live' ? 'Live model response' : 'Response mode unavailable'}</span>
      </div>
      <h2 id="answer-heading" ref={headingRef} tabIndex={-1}>{message.question}</h2>
      <p className="answer-text">{message.answer}</p>
      <p className="answer-reason">{message.reason}</p>
      {message.sources.length > 0 ? (
        <section className="answer-sources" aria-label="Cited source excerpts">
          <h3>Check the evidence <span>{message.sources.length} cited {message.sources.length === 1 ? 'excerpt' : 'excerpts'}</span></h3>
          {message.sources.map(source => <SourceCard key={source.chunk_id} source={source} />)}
        </section>
      ) : (
        <p className="no-sources">No supporting citations. Try a sample question or inspect the documents.</p>
      )}
      <p className="query-reference">Query reference <span>{message.query_id}</span></p>
    </article>
  )
}
