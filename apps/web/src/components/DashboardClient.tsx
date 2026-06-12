"use client";

import { useEffect, useMemo, useState } from "react";

import { approveTask, createTask, getTask, listProperties, listTasks, rejectTask } from "../api";
import { demoLogs, demoProperties, demoTask } from "../demoData";
import type { Property, TaskLog, TaskRun } from "../types";
import { ApprovalModal } from "./ApprovalModal";
import { AuditTimeline } from "./AuditTimeline";
import { PropertyGrid } from "./PropertyGrid";
import { TaskComposer } from "./TaskComposer";
import { TaskPanel } from "./TaskPanel";

export function DashboardClient() {
  const [properties, setProperties] = useState<Property[]>(demoProperties);
  const [tasks, setTasks] = useState<TaskRun[]>([demoTask]);
  const [logs, setLogs] = useState<TaskLog[]>(demoLogs);
  const [apiState, setApiState] = useState<"demo" | "live">("demo");

  useEffect(() => {
    let active = true;
    async function load() {
      try {
        const [propertyData, taskData] = await Promise.all([listProperties(), listTasks()]);
        if (!active) return;
        setProperties(propertyData);
        const normalizedTasks = taskData.length > 0 ? taskData : [demoTask];
        setTasks(normalizedTasks);
        setApiState("live");
        const firstTask = normalizedTasks[0];
        if (firstTask) {
          const detail = await getTask(firstTask.id);
          if (active) setLogs(detail.logs.length > 0 ? detail.logs : demoLogs);
        }
      } catch {
        setApiState("demo");
      }
    }
    load();
    const timer = window.setInterval(load, 5000);
    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, []);

  const waitingTask = useMemo(() => tasks.find((task) => task.approval_required), [tasks]);

  async function handleCreateTask(propertyId: string, task: string) {
    const created = apiState === "live" ? await createTask(propertyId, task) : demoTask;
    setTasks((current) => [created, ...current.filter((item) => item.id !== created.id)]);
    if (apiState === "live") {
      const detail = await getTask(created.id);
      setLogs(detail.logs);
    }
  }

  async function handleApprove(taskId: string) {
    let updated: TaskRun;
    try {
      updated = await approveTask(taskId);
    } catch {
      updated = { ...demoTask, status: "completed" as const, approval_required: false, final_summary: "Owner approved the repair. Maintenance Agent finalized the repair approval." };
    }
    setTasks((current) => current.map((task) => (task.id === taskId ? updated : task)));
  }

  async function handleReject(taskId: string) {
    let updated: TaskRun;
    try {
      updated = await rejectTask(taskId);
    } catch {
      updated = { ...demoTask, status: "rejected" as const, approval_required: false, final_summary: "Owner rejected the repair. No spending commitment was made." };
    }
    setTasks((current) => current.map((task) => (task.id === taskId ? updated : task)));
  }

  return (
    <div className="appShell">
      <aside className="navRail">
        <div className="brandMark">⌂</div>
        <nav>
          <span className="active">Command Center</span>
          <span>Properties</span>
          <span>Agents</span>
          <span>Tasks</span>
          <span>Approvals</span>
          <span>Audit Trail</span>
        </nav>
        <div className="systemCard">
          <strong>System Status</strong>
          <span>Agents Online 5 / 5</span>
        </div>
      </aside>
      <main className="dashboard">
        <header className="topbar">
          <div>
            <h1>Agentic Property Operations</h1>
          </div>
          <div className="topbarActions">
            <span className={`livePill ${apiState}`}>{apiState === "live" ? "Live API" : "Demo data"}</span>
            <span className="avatar">AM</span>
            <span>Alex Morgan</span>
          </div>
        </header>
        <div className="layout">
          <div className="mainColumn">
            <PropertyGrid properties={properties} />
            <AuditTimeline logs={logs} />
          </div>
          <aside className="sideColumn">
            <TaskComposer properties={properties} onCreateTask={handleCreateTask} />
            <TaskPanel tasks={tasks} />
            <ApprovalModal task={waitingTask} onApprove={handleApprove} onReject={handleReject} />
          </aside>
        </div>
      </main>
    </div>
  );
}
