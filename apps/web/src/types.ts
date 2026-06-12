export type PropertyStatus = "healthy" | "attention" | "approval_required";
export type TaskStatus = "queued" | "running" | "waiting_approval" | "approved" | "rejected" | "completed" | "failed";

export type Property = {
  id: string;
  name: string;
  address: string;
  status: PropertyStatus;
  notes: string;
};

export type ApprovalRequest = {
  id: string;
  task_id: string;
  action: string;
  details: string;
  cost_estimate: number | null;
  risk: string;
  decision: "pending" | "approved" | "rejected";
  created_at: string;
};

export type TaskRun = {
  id: string;
  property_id: string;
  task: string;
  status: TaskStatus;
  agent_name: string;
  messages: string[];
  approval_required: boolean;
  approval_request: ApprovalRequest | null;
  final_summary: string | null;
  error: string | null;
  created_at: string;
  updated_at: string;
};

export type TaskLog = {
  id: string;
  task_id: string;
  property_id: string;
  node: string;
  agent_name: string;
  status: TaskStatus;
  message: string;
  created_at: string;
};

