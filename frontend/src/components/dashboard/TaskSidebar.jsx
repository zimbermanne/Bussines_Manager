import React from 'react';

function SpinnerIcon() {
  return (
    <svg className="task-icon task-icon-spinner" width="16" height="16" viewBox="0 0 16 16" fill="none">
      <circle cx="8" cy="8" r="6" stroke="currentColor" strokeWidth="1.5" strokeDasharray="28" strokeDashoffset="8" />
    </svg>
  );
}

function CheckIcon() {
  return (
    <svg className="task-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
      <circle cx="8" cy="8" r="7" stroke="currentColor" strokeWidth="1.2" />
      <path d="M5 8l2 2 4-4" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function TaskRow({ task, isActive, onSelect }) {
  return (
    <div
      className={`task-item${isActive ? ' active' : ''}`}
      onClick={() => onSelect(task.id)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onSelect(task.id)}
    >
      {task.status === 'in_progress' ? <SpinnerIcon /> : <CheckIcon />}
      <div className="task-details">
        <div className="task-header">
          <span className="task-title">{task.title}</span>
          {task.time && <span className="task-meta">{task.time}</span>}
        </div>
        {task.subtext && <div className="task-subtext">{task.subtext}</div>}
        {task.diff && (
          <div className="task-diff">
            <span className="addition">+{task.diff.add}</span>
            <span className="subtraction">-{task.diff.remove}</span>
          </div>
        )}
      </div>
    </div>
  );
}

export default function TaskSidebar({ inProgress, readyForReview, selectedId, onSelect }) {
  return (
    <aside className="task-sidebar">
      <div className="sidebar-section">
        <div className="sidebar-section-title">
          In progress <span className="section-count">{inProgress.length}</span>
        </div>
        {inProgress.map((task) => (
          <TaskRow key={task.id} task={task} isActive={selectedId === task.id} onSelect={onSelect} />
        ))}
      </div>

      <div className="sidebar-section">
        <div className="sidebar-section-title">
          Ready for review <span className="section-count">{readyForReview.length}</span>
        </div>
        {readyForReview.map((task) => (
          <TaskRow key={task.id} task={task} isActive={selectedId === task.id} onSelect={onSelect} />
        ))}
      </div>
    </aside>
  );
}
