import type { TaskLog } from "../types";

const auditTimeFormatter = new Intl.DateTimeFormat("en-GB", {
  hour: "2-digit",
  minute: "2-digit",
  hour12: false,
  timeZone: "UTC"
});

function formatAuditTime(timestamp: string) {
  return auditTimeFormatter.format(new Date(timestamp));
}

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
            <time>{formatAuditTime(log.created_at)}</time>
            <strong>{log.agent_name}</strong>
            <span className={`badge ${log.status}`}>{log.status.replace("_", " ")}</span>
            <p>{log.message}</p>
          </li>
        ))}
      </ol>
    </section>
  );
}
