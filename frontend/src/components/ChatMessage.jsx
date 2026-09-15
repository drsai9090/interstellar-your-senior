import SourceCard from './SourceCard'

const STATUS_LABELS = {
  supported: 'Supported',
  partial: 'Partially supported',
  unsupported: 'Unsupported',
}

export default function ChatMessage({ message, headingRef }) {
  return (
    <article className="answer-card" aria-labelledby="answer-heading">
      <div className="answer-topline">
        <span className={`support-badge support-${message.status}`}>
          <span aria-hidden="true">{message.status === 'supported' ? '✓' : '!'}</span>
          {STATUS_LABELS[message.status] || 'Support status unavailable'}
        </span>
        <span className="answer-mode">{message.response_mode === 'fixture' ? 'Prewritten answer' : message.response_mode === 'live' ? 'Live response' : 'Response mode unavailable'}</span>
      </div>
      <h2 id="answer-heading" ref={headingRef} tabIndex={-1}>{message.question}</h2>
      <p className="answer-text">{message.answer}</p>
      <p className="answer-reason">{message.reason}</p>
      {message.sources.length > 0 ? (
        <section className="answer-sources" aria-label="Cited source excerpts">
          <h3>Sources <span>{message.sources.length}</span></h3>
          {message.sources.map(source => <SourceCard key={source.chunk_id} source={source} />)}
        </section>
      ) : (
        <p className="no-sources">No supporting sources.</p>
      )}
    </article>
  )
}
