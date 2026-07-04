import { NextResponse } from 'next/server';

// Rate limiting per-IP sederhana (in-memory, sliding window).
// Menahan brute-force / flooding. Untuk skala besar / multi-instance,
// gunakan store terpusat (mis. Redis/Upstash) — ini cukup untuk 1 instance.
const WINDOW_MS = 60_000; // jendela 1 menit
const MAX_REQUESTS = 100; // maksimum request per IP per jendela

const hits = new Map(); // ip -> number[] (timestamp request)

function getClientIp(req) {
  // Cloudflare mengirim IP asli klien di header ini.
  return (
    req.headers.get('cf-connecting-ip') ||
    req.headers.get('x-forwarded-for')?.split(',')[0]?.trim() ||
    'unknown'
  );
}

export function middleware(req) {
  const ip = getClientIp(req);
  const now = Date.now();

  const timestamps = (hits.get(ip) || []).filter((t) => now - t < WINDOW_MS);
  timestamps.push(now);
  hits.set(ip, timestamps);

  // Bersihkan map sesekali agar tidak bocor memori.
  if (hits.size > 10_000) {
    for (const [key, ts] of hits) {
      if (ts.every((t) => now - t >= WINDOW_MS)) hits.delete(key);
    }
  }

  if (timestamps.length > MAX_REQUESTS) {
    return new NextResponse('Too Many Requests', {
      status: 429,
      headers: {
        'Retry-After': String(Math.ceil(WINDOW_MS / 1000)),
        'Content-Type': 'text/plain',
      },
    });
  }

  return NextResponse.next();
}

export const config = {
  // Terapkan ke semua route kecuali aset statis Next.js & favicon.
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
