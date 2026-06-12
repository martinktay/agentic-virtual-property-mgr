import type { Property, TaskLog, TaskRun } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_AGENT_API_URL ?? "http://127.0.0.1:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "content-type": "application/json",
      ...(init?.headers ?? {})
    },
    cache: "no-store"
  });
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function listProperties(): Promise<Property[]> {
  return request<Property[]>("/properties");
}

export function listTasks(): Promise<TaskRun[]> {
  return request<TaskRun[]>("/tasks");
}

export function getTask(taskId: string): Promise<{ task: TaskRun; logs: TaskLog[] }> {
  return request<{ task: TaskRun; logs: TaskLog[] }>(`/tasks/${taskId}`);
}

export function createTask(propertyId: string, task: string): Promise<TaskRun> {
  return request<TaskRun>("/tasks", {
    method: "POST",
    body: JSON.stringify({ property_id: propertyId, task })
  });
}

export function approveTask(taskId: string): Promise<TaskRun> {
  return request<TaskRun>(`/tasks/${taskId}/approve`, { method: "POST" });
}

export function rejectTask(taskId: string): Promise<TaskRun> {
  return request<TaskRun>(`/tasks/${taskId}/reject`, { method: "POST" });
}

