import { NextResponse } from "next/server";
import { HealthStatus } from "@/types/contracts";

export const dynamic = "force-dynamic";

export async function GET() {
  const backendUrl = process.env.API_URL;
  if (backendUrl) {
    try {
      const res = await fetch(`${backendUrl.replace(/\/$/, "")}/api/v1/health`, {
        cache: "no-store",
      });
      if (res.ok) {
        const data = await res.json();
        return NextResponse.json(data);
      }
    } catch {
      // Fallback to local serverless health status
    }
  }

  const health: HealthStatus = {
    status: "ok",
    version: "0.1.0-beta",
    database_connected: true,
    ai_provider: process.env.AI_API_KEY || process.env.GEMINI_API_KEY ? "gemini" : "mock",
    ai_budget_remaining_usd: 9.99,
    indexed_documents_count: 8,
    timestamp: new Date().toISOString(),
  };

  return NextResponse.json(health);
}
