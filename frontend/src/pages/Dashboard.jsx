import React, { useEffect, useState } from 'react';
import TaskSidebar from '../components/dashboard/TaskSidebar';
import ActivityStream from '../components/dashboard/ActivityStream';
import Composer from '../components/dashboard/Composer';
import { IN_PROGRESS, READY_FOR_REVIEW, TASK_DETAILS } from '../data/agentTasks';

export default function Dashboard() {
  const [selectedId, setSelectedId] = useState('build-landing-page');
  const selectedTask = TASK_DETAILS[selectedId];

  useEffect(() => {
    document.body.classList.add('layout-dashboard');
    return () => document.body.classList.remove('layout-dashboard');
  }, []);

  return (
    <div className="app-container">
      <TaskSidebar
        inProgress={IN_PROGRESS}
        readyForReview={READY_FOR_REVIEW}
        selectedId={selectedId}
        onSelect={setSelectedId}
      />

      <section className="workspace">
        <header className="workspace-header">
          <h1 className="workspace-title">{selectedTask?.title ?? 'Dashboard'}</h1>
        </header>

        <ActivityStream task={selectedTask} />
        <Composer />
      </section>
    </div>
  );
}
