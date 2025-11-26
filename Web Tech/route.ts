import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"
import { connectToDatabase } from "@/lib/mongodb"

export async function POST(request: NextRequest) {
  try {
    const { name, email } = await request.json()

    if (!name || !email) {
      return NextResponse.json({ error: "Missing name or email" }, { status: 400 })
    }

    const { db } = await connectToDatabase()

    const users = db.collection("users")

    const existing = await users.findOne({ email })
    if (existing) {
      // Optionally update name if changed
      await users.updateOne({ email }, { $set: { name, updatedAt: new Date() } })
      return NextResponse.json({ success: true, message: "User updated" })
    }

    const result = await users.insertOne({ name, email, createdAt: new Date() })

    return NextResponse.json({ success: true, id: result.insertedId })
  } catch (err) {
    console.error("[v0] Error saving user:", err)
    return NextResponse.json({ error: "Failed to save user" }, { status: 500 })
  }
}
