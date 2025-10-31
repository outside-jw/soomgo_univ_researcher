/**
 * Assignment Card Component
 * Displays the original assignment/problem that the learner is working on
 */
import './AssignmentCard.css';

interface Props {
  assignmentText: string;
}

export default function AssignmentCard({ assignmentText }: Props) {
  if (!assignmentText) return null;

  return (
    <div className="assignment-card">
      <div className="assignment-header">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" className="assignment-icon">
          <path
            d="M10 0C4.48 0 0 4.48 0 10s4.48 10 10 10 10-4.48 10-10S15.52 0 10 0zM9 15H7V9h2v6zm0-8H7V5h2v2z"
            fill="currentColor"
          />
          <path
            d="M14 15h-2V5h2v10z"
            fill="currentColor"
          />
        </svg>
        <h3 className="assignment-title">현재 과제</h3>
      </div>
      <div className="assignment-content">
        <p>{assignmentText}</p>
      </div>
    </div>
  );
}
