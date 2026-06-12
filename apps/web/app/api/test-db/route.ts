import { NextResponse } from "next/server";
import { Client } from "pg";

export const runtime = "nodejs";

export async function GET() {
  const connectionString = process.env.DATABASE_URL;

  if (!connectionString) {
    return NextResponse.json(
      {
        ok: false,
        service: "aurora-dsql",
        error: "DATABASE_URL is not configured"
      },
      { status: 503 }
    );
  }

  const client = new Client({
    connectionString,
    ssl: { rejectUnauthorized: true }
  });

  try {
    await client.connect();
    const result = await client.query("SELECT NOW() AS now");
    return NextResponse.json({
      ok: true,
      service: "aurora-dsql",
      timestamp: result.rows[0]?.now
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown database error";
    return NextResponse.json(
      {
        ok: false,
        service: "aurora-dsql",
        error: message
      },
      { status: 500 }
    );
  } finally {
    await client.end();
  }
}
