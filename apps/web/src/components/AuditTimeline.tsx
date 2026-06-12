import type { TaskLog } from "../types";

export function AuditTimeline({ logs }: { logs: TaskLog[] }) {
  return (
    <section className="surface timelineSurface">
      <div className="sectionHeader">
        <div>
          <h2>Audit Timeline</h2>
          <p>Node-by-node record of multi-agent orchestration</p>
        </div>
      </div>
      <ol className="timeline">
        {logs.map((log) => (
          <li key={log.id}>
            <span className={`nodeDot ${log.status}`} />
            <time>{new Date(log.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</time>
            <strong>{log.agent_name}</strong>
            <span className={`badge ${log.status}`}>{log.status.replace("_", " ")}</span>
            <p>{log.message}</p>
          </li>
        ))}
      </ol>
    </section>
  );
}

