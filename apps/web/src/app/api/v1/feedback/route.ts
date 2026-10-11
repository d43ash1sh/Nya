import { NextRequest, NextResponse } from "next/server";
import crypto from "crypto";

export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const query = body.query || "";
    
    // Privacy-preserving query hash (SHA-256)
    const hashedQuery = crypto.createHash("sha256").update(query).digest("hex");
    
    // In serverless, feedback is safely acknowledged and logged without raw PII
    console.info(`[NYA-FEEDBACK] Query Hash: ${hashedQuery.slice(0, 16)} Type: ${body.feedback_type}`);

    return NextResponse.json({
      success: true,
      message: "Feedback submitted anonymously. Thank you for improving ঞ (Nya)!",
    });
  } catch (error) {
    return NextResponse.json(
      { success: false, message: "Invalid feedback payload." },
      { status: 400 }
    );
  }
}
