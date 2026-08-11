import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({ status: 'Auth disabled in dev mode' });
}

export async function POST() {
  return NextResponse.json({ status: 'Auth disabled in dev mode' });
}
