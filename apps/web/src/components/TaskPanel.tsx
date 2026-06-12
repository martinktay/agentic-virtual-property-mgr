import type { TaskRun } from "../types";

export function TaskPanel({ tasks }: { tasks: TaskRun[] }) {
  return (
    <section className="surface">
      <div className="sectionHeader">
        <h2>Active Tasks</h2>
      </div>
      <div className="taskList">
        {tasks.map((task) => (
          <article className="taskRow" key={task.id}>
            <div>
              <h3>{task.task}</h3>
              <p>Assigned to: {task.agent_name}</p>
            </div>
            <span className={`badge ${task.status}`}>
              {task.approval_required ? "Requires Approval" : task.status.replace("_", " ")}
            </span>
          </article>
        ))}
      </div>
    </section>
  );
}

