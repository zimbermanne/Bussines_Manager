import React, { useState } from 'react';

export default function Composer() {
  const [value, setValue] = useState('');

  return (
    <div className="composer-sticky-wrapper">
      <div className="composer-box">
        <textarea
          className="composer-textarea"
          placeholder="Plan, search, build anything..."
          rows={2}
          value={value}
          onChange={(e) => setValue(e.target.value)}
        />
        <div className="composer-footer">
          <div className="composer-pills-group">
            <button type="button" className="pill-selector">
              <span className="pill-icon">∞</span> Agent
            </button>
            <button type="button" className="pill-selector">
              Composer 2.5
              <svg width="10" height="10" viewBox="0 0 10 10" fill="currentColor">
                <path d="M2 4l3 3 3-3" stroke="currentColor" strokeWidth="1.2" fill="none" />
              </svg>
            </button>
          </div>
          <button
            type="button"
            className={`btn-submit-circle${value.trim() ? ' active' : ''}`}
            aria-label="Submit"
          >
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M7 3v8M4 6l3-3 3 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
