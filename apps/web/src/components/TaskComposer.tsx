"use client";

import { useState } from "react";

import type { Property } from "../types";

type Props = {
  properties: Property[];
  onCreateTask: (propertyId: string, task: string) => void;
};

const defaultTask = "Power is out at Property B and the electrician quoted 850 pounds for an emergency repair.";

export function TaskComposer({ properties, onCreateTask }: Props) {
  const defaultProperty = properties.find((property) => property.id === "prop-b") ?? properties[0];
  const [propertyId, setPropertyId] = useState(defaultProperty?.id ?? "");
  const [task, setTask] = useState(defaultTask);

  return (
    <section className="surface">
      <div className="sectionHeader">
        <h2>Start Agent Task</h2>
      </div>
      <form className="composer">
        <label>
          Select Property
          <select value={propertyId} onChange={(event) => setPropertyId(event.target.value)}>
            {properties.map((property) => (
              <option value={property.id} key={property.id}>
                {property.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Describe Task
          <textarea value={task} onChange={(event) => setTask(event.target.value)} />
        </label>
        <button type="button" className="primary" onClick={() => onCreateTask(propertyId, task)}>
          Run Agents
        </button>
      </form>
    </section>
  );
}

