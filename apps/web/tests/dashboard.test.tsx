import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { AuditTimeline } from "../src/components/AuditTimeline";
import { DashboardClient } from "../src/components/DashboardClient";
import * as api from "../src/api";

vi.mock("../src/api", () => ({
  listProperties: vi.fn(async () => {
    throw new Error("use demo data");
  }),
  listTasks: vi.fn(async () => []),
  getTask: vi.fn(async () => ({ task: null, logs: [] })),
  createTask: vi.fn(),
  approveTask: vi.fn(async (taskId: string) => ({
    id: taskId,
    property_id: "prop-b",
    task: "Power is out at Property B and the electrician quoted 850 pounds for an emergency repair.",
    status: "completed",
    agent_name: "MaintenanceAgent",
    messages: [],
    approval_required: false,
    approval_request: null,
    final_summary: "Owner approved the repair.",
    error: null,
    created_at: "2026-06-12T10:24:12Z",
    updated_at: "2026-06-12T10:25:12Z"
  })),
  rejectTask: vi.fn()
}));

describe("dashboard", () => {
  it("renders the operations dashboard with approval state", async () => {
    render(<DashboardClient />);

    expect(await screen.findByRole("heading", { name: /agentic property operations/i })).toBeInTheDocument();
    expect(screen.getAllByText("Property B").length).toBeGreaterThan(0);
    expect(screen.getByText(/Requires Approval/i)).toBeInTheDocument();
    expect(screen.getAllByText(/ComplianceAgent/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/Workflow paused for owner approval/i)).toBeInTheDocument();
  });

  it("calls approve when the approval button is clicked", async () => {
    const user = userEvent.setup();
    render(<DashboardClient />);

    await user.click(await screen.findByRole("button", { name: /approve/i }));

    expect(api.approveTask).toHaveBeenCalledWith("task-demo");
  });

  it("formats audit timestamps deterministically for hydration", () => {
    render(
      <AuditTimeline
        logs={[
          {
            id: "log-test",
            task_id: "task-demo",
            property_id: "prop-b",
            node: "human_review",
            agent_name: "Owner",
            status: "waiting_approval",
            message: "Workflow paused for owner approval.",
            created_at: "2026-06-12T10:24:18Z"
          }
        ]}
      />
    );

    expect(screen.getByText("10:24")).toBeInTheDocument();
  });
});
