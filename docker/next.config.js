/** @type {import('next').NextConfig} */
const securityHeaders = [
  // Cegah MIME sniffing
  { key: 'X-Content-Type-Options', value: 'nosniff' },
  // Cegah clickjacking (situs tidak bisa di-embed di iframe orang lain)
  { key: 'X-Frame-Options', value: 'DENY' },
  // Batasi informasi referrer yang bocor ke pihak lain
  { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
  // Paksa HTTPS selama 2 tahun (aman karena diakses via Cloudflare/HTTPS)
  {
    key: 'Strict-Transport-Security',
    value: 'max-age=63072000; includeSubDomains; preload',
  },
  // Matikan akses fitur browser sensitif secara default
  {
    key: 'Permissions-Policy',
    value: 'camera=(), microphone=(), geolocation=(), interest-cohort=()',
  },
  // Content Security Policy — batasi sumber konten agar tahan XSS.
  // 'unsafe-inline' pada style diperlukan karena halaman memakai inline style.
  {
    key: 'Content-Security-Policy',
    value: [
      "default-src 'self'",
      "script-src 'self'",
      "style-src 'self' 'unsafe-inline'",
      "img-src 'self' data:",
      "font-src 'self'",
      "connect-src 'self'",
      "frame-ancestors 'none'",
      "base-uri 'self'",
      "form-action 'self'",
    ].join('; '),
  },
];

const nextConfig = {
  output: 'standalone',
  // Sembunyikan header X-Powered-By: Next.js (kurangi fingerprinting)
  poweredByHeader: false,
  async headers() {
    return [{ source: '/:path*', headers: securityHeaders }];
  },
};

module.exports = nextConfig;
