import type { Property } from "../types";

export function PropertyGrid({ properties }: { properties: Property[] }) {
  return (
    <section className="surface">
      <div className="sectionHeader">
        <div>
          <h2>Property Overview</h2>
          <p>Real-time status of managed properties</p>
        </div>
      </div>
      <div className="propertyGrid">
        {properties.map((property) => (
          <article className="propertyCard" key={property.id}>
            <div className="cardTitle">
              <h3>{property.name}</h3>
              <span className={`badge ${property.status}`}>{property.status.replace("_", " ")}</span>
            </div>
            <p className="address">{property.address}</p>
            <div className="metrics">
              <span>Occupancy <strong>{property.id === "prop-b" ? "87%" : "96%"}</strong></span>
              <span>Open Tasks <strong>{property.id === "prop-b" ? "7" : "2"}</strong></span>
              <span>Overdue <strong>{property.id === "prop-b" ? "2" : "0"}</strong></span>
            </div>
            <p>{property.notes}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

