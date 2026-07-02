export async function getServerSideProps({ req }) {
  // Header yang diinjeksi Cloudflare saat trafik lewat tunnel.
  const cfRay = req.headers['cf-ray'] || null;
  const cfIp = req.headers['cf-connecting-ip'] || null;
  const cfCountry = req.headers['cf-ipcountry'] || null;
  const viaCloudflare = Boolean(cfRay);

  return {
    props: {
      viaCloudflare,
      cfRay,
      cfIp,
      cfCountry,
      now: new Date().toISOString(),
    },
  };
}

export default function Home({ viaCloudflare, cfRay, cfIp, cfCountry, now }) {
  return (
    <main
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#0b0f19',
        color: '#e6edf3',
        fontFamily: 'system-ui, sans-serif',
        padding: '2rem',
      }}
    >
      <div
        style={{
          maxWidth: 520,
          width: '100%',
          background: '#111827',
          border: '1px solid #1f2937',
          borderRadius: 16,
          padding: '2rem',
          boxShadow: '0 10px 40px rgba(0,0,0,0.4)',
        }}
      >
        <h1 style={{ margin: '0 0 0.5rem', fontSize: '1.6rem' }}>🚀 App is live</h1>
        <p style={{ color: '#9ca3af', margin: '0 0 1.5rem' }}>
          Next.js + Docker + Cloudflare Tunnel
        </p>

        <div
          style={{
            display: 'inline-block',
            padding: '0.35rem 0.8rem',
            borderRadius: 999,
            fontSize: '0.85rem',
            fontWeight: 600,
            background: viaCloudflare ? '#0f2f1f' : '#2f1f0f',
            color: viaCloudflare ? '#4ade80' : '#fbbf24',
            border: `1px solid ${viaCloudflare ? '#166534' : '#92400e'}`,
            marginBottom: '1.5rem',
          }}
        >
          {viaCloudflare
            ? '✅ Diakses via Cloudflare (IP origin tersembunyi)'
            : '⚠️ Akses langsung (bukan lewat Cloudflare)'}
        </div>

        <dl style={{ display: 'grid', gap: '0.6rem', margin: 0 }}>
          <Row label="Cloudflare Ray" value={cfRay || '—'} />
          <Row label="Your IP (via CF)" value={cfIp || '—'} />
          <Row label="Country" value={cfCountry || '—'} />
          <Row label="Server time" value={now} />
        </dl>
      </div>
    </main>
  );
}

function Row({ label, value }) {
  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'space-between',
        gap: '1rem',
        padding: '0.5rem 0',
        borderBottom: '1px solid #1f2937',
        fontSize: '0.9rem',
      }}
    >
      <dt style={{ color: '#9ca3af' }}>{label}</dt>
      <dd style={{ margin: 0, fontFamily: 'monospace', wordBreak: 'break-all' }}>
        {value}
      </dd>
    </div>
  );
}
