import type { TaskRun } from "../types";

type Props = {
  task: TaskRun | undefined;
  onApprove: (taskId: string) => void;
  onReject: (taskId: string) => void;
};

export function ApprovalModal({ task, onApprove, onReject }: Props) {
  if (!task?.approval_request) {
    return (
      <section className="approvalPanel">
        <h2>Human-in-the-loop Approval</h2>
        <p>No owner decisions are waiting.</p>
      </section>
    );
  }

  return (
    <section className="approvalPanel" aria-label="Approval request">
      <h2>Human-in-the-loop Approval</h2>
      <div className="approvalMeta">
        <span>Task</span>
        <strong>{task.approval_request.details}</strong>
      </div>
      <div className="approvalStats">
        <div>
          <span>Estimated Cost</span>
          <strong>£{task.approval_request.cost_estimate ?? 0}</strong>
        </div>
        <div>
          <span>Risk Level</span>
          <strong>Medium</strong>
        </div>
      </div>
      <p><strong>Risk Summary:</strong> {task.approval_request.risk}</p>
      <div className="modalActions">
        <button type="button" className="reject" onClick={() => onReject(task.id)}>Reject</button>
        <button type="button" className="primary" onClick={() => onApprove(task.id)}>Approve</button>
      </div>
    </section>
  );
}

