export default function SourceCard({ source }) {
  return (
    <details className="source-card" open>
      <summary aria-label={`Citation ${source.chunk_id} from ${source.source_file}`}>
        <span className="source-file">{source.source_file}</span>
        <span className="citation-id">[{source.chunk_id}]</span>
      </summary>
      <div className="source-content">
        {source.section_heading && <p className="source-section">{source.section_heading}</p>}
        <blockquote>{source.content}</blockquote>
        <p className="source-meta">
          {source.source_type && <span>{source.source_type.toUpperCase()}</span>}
          {source.page_number != null && <span>Page {source.page_number}</span>}
          {source.author && <span>{source.author}</span>}
        </p>
      </div>
    </details>
  )
}
