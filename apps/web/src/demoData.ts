import type { Property, TaskLog, TaskRun } from "./types";

export const demoProperties: Property[] = [
  {
    id: "prop-a",
    name: "Property A",
    address: "12 Market Street, London",
    status: "healthy",
    notes: "Executive short-let with upcoming guest arrival."
  },
  {
    id: "prop-b",
    name: "Property B",
    address: "4 Riverside Walk, Manchester",
    status: "attention",
    notes: "Power issue reported by current guest. Emergency repair may be needed."
  },
  {
    id: "prop-c",
    name: "Property C",
    address: "77 Harbour Road, Bristol",
    status: "healthy",
    notes: "Routine turnover completed."
  }
];

export const demoTask: TaskRun = {
  id: "task-demo",
  property_id: "prop-b",
  task: "Power is out at Property B and the electrician quoted 850 pounds for an emergency repair.",
  status: "waiting_approval",
  agent_name: "ComplianceAgent",
  messages: [
    "Orchestrator routed task to maintenance.",
    "Maintenance Agent triaged the incident and prepared an emergency repair recommendation.",
    "Finance Agent reviewed the cost impact. Estimated cost: 850 pounds.",
    "Compliance Agent requires human approval before committing spend."
  ],
  approval_required: true,
  approval_request: {
    id: "approval-demo",
    task_id: "task-demo",
    action: "approve_maintenance_cost",
    details: "Power is out at Property B and the electrician quoted 850 pounds for an emergency repair.",
    cost_estimate: 850,
    risk: "Owner approval required before high-cost repair can proceed.",
    decision: "pending",
    created_at: "2026-06-12T10:24:18Z"
  },
  final_summary: null,
  error: null,
  created_at: "2026-06-12T10:24:12Z",
  updated_at: "2026-06-12T10:24:18Z"
};

export const demoLogs: TaskLog[] = [
  {
    id: "log-1",
    task_id: "task-demo",
    property_id: "prop-b",
    node: "orchestrator",
    agent_name: "OrchestratorManager",
    status: "running",
    message: "Routed power outage task to Maintenance.",
    created_at: "2026-06-12T10:24:12Z"
  },
  {
    id: "log-2",
    task_id: "task-demo",
    property_id: "prop-b",
    node: "maintenance",
    agent_name: "MaintenanceAgent",
    status: "running",
    message: "Triaged outage and prepared emergency repair recommendation.",
    created_at: "2026-06-12T10:24:13Z"
  },
  {
    id: "log-3",
    task_id: "task-demo",
    property_id: "prop-b",
    node: "finance",
    agent_name: "FinanceAgent",
    status: "running",
    message: "Validated repair quote. Estimated cost: 850 pounds.",
    created_at: "2026-06-12T10:24:15Z"
  },
  {
    id: "log-4",
    task_id: "task-demo",
    property_id: "prop-b",
    node: "compliance",
    agent_name: "ComplianceAgent",
    status: "running",
    message: "High-cost repair requires owner approval.",
    created_at: "2026-06-12T10:24:17Z"
  },
  {
    id: "log-5",
    task_id: "task-demo",
    property_id: "prop-b",
    node: "human_review",
    agent_name: "Owner",
    status: "waiting_approval",
    message: "Workflow paused for owner approval.",
    created_at: "2026-06-12T10:24:18Z"
  }
];

