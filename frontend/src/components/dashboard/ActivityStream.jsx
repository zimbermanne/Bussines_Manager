import React from 'react';

function FileBadge({ path, added, removed }) {
  return (
    <div className="file-badge-card">
      <span className="file-path">{path}</span>
      <span className="diff-stat">
        <span className="addition">+{added}</span>
        <span className="subtraction">-{removed}</span>
      </span>
    </div>
  );
}

function MetaLog({ children }) {
  return <div className="meta-log-line">{children}</div>;
}

export default function ActivityStream({ task }) {
  if (!task) {
    return (
      <div className="stream-container stream-empty">
        <p>Select a task to view its activity</p>
      </div>
    );
  }

  return (
    <div className="stream-container">
      {task.prompt && (
        <div className="user-prompt-bubble">{task.prompt}</div>
      )}

      {task.meta?.map((line, i) => (
        <MetaLog key={i}>{line}</MetaLog>
      ))}

      {task.response && (
        <p className="agent-response">{task.response}</p>
      )}

      {task.files?.map((file) => (
        <FileBadge key={file.path} path={file.path} added={file.added} removed={file.removed} />
      ))}

      {task.summary && (
        <p className="agent-summary">{task.summary}</p>
      )}
    </div>
  );
}
