import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json(
    { message: 'Authentication is managed directly by the MemeGPT FastAPI backend at /api/v1/auth' },
    { status: 404 }
  );
}

export async function POST() {
  return NextResponse.json(
    { message: 'Authentication is managed directly by the MemeGPT FastAPI backend at /api/v1/auth' },
    { status: 404 }
  );
}
