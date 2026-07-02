import Head from 'next/head';

export default function Home() {
  return (
    <div style={styles.container}>
      <Head>
        <title>Next.js Docker Test - Ready for Railway</title>
        <meta name="description" content="Dockerized Next.js app running on Debian, ready for Railway and GHCR deployment test." />
        <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🐳</text></svg>" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="true" />
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet" />
      </Head>

      <main style={styles.main}>
        <div style={styles.glow1}></div>
        <div style={styles.glow2}></div>

        <div style={styles.card}>
          <div style={styles.badgeContainer}>
            <span style={styles.badge}>Debian Base</span>
            <span style={styles.badgeRailway}>Railway Ready</span>
          </div>

          <h1 style={styles.title}>
            Next.js <span style={styles.gradientText}>Dockerized</span>
          </h1>

          <p style={styles.subtitle}>
            Aplikasi uji coba Next.js berhasil berjalan di dalam Docker container menggunakan base image <strong>Debian</strong>.
          </p>

          <div style={styles.statusBox}>
            <div style={styles.statusHeader}>
              <span style={styles.statusDot}></span>
              <span style={styles.statusText}>Status: Container Aktif</span>
            </div>
            <p style={styles.statusDetails}>
              Image di-build melalui GHCR dan dideploy secara otomatis ke Railway.
            </p>
          </div>

          <div style={styles.stepsContainer}>
            <h3 style={styles.stepsTitle}>Langkah Uji Coba Selanjutnya:</h3>
            <ol style={styles.stepsList}>
              <li style={styles.stepItem}>
                <span style={styles.stepNum}>1</span>
                <span>Timpa direktori ini dengan source-code Next.js Anda sendiri.</span>
              </li>
              <li style={styles.stepItem}>
                <span style={styles.stepNum}>2</span>
                <span>Push kode Anda ke repository GitHub Anda.</span>
              </li>
              <li style={styles.stepItem}>
                <span style={styles.stepNum}>3</span>
                <span>GitHub Actions akan otomatis build & push ke <strong>GHCR</strong>.</span>
              </li>
              <li style={styles.stepItem}>
                <span style={styles.stepNum}>4</span>
                <span>Railway akan mendeteksi update di GHCR dan mendeploy image baru.</span>
              </li>
            </ol>
          </div>

          <div style={styles.footer}>
            Created by Antigravity AI &bull; dockerAiCosmoz
          </div>
        </div>
      </main>
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    background: '#0B0F19',
    fontFamily: "'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    color: '#F3F4F6',
    position: 'relative',
    overflow: 'hidden',
  },
  main: {
    padding: '2rem 1rem',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    width: '100%',
    maxWidth: '600px',
    zIndex: 2,
  },
  glow1: {
    position: 'absolute',
    top: '10%',
    left: '10%',
    width: '300px',
    height: '300px',
    background: 'radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, rgba(99, 102, 241, 0) 70%)',
    borderRadius: '50%',
    filter: 'blur(40px)',
    zIndex: 1,
  },
  glow2: {
    position: 'absolute',
    bottom: '10%',
    right: '10%',
    width: '350px',
    height: '350px',
    background: 'radial-gradient(circle, rgba(6, 182, 212, 0.15) 0%, rgba(6, 182, 212, 0) 70%)',
    borderRadius: '50%',
    filter: 'blur(50px)',
    zIndex: 1,
  },
  card: {
    background: 'rgba(17, 24, 39, 0.7)',
    backdropFilter: 'blur(16px)',
    WebkitBackdropFilter: 'blur(16px)',
    border: '1px solid rgba(255, 255, 255, 0.08)',
    borderRadius: '24px',
    padding: '2.5rem',
    width: '100%',
    boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
    display: 'flex',
    flexDirection: 'column',
  },
  badgeContainer: {
    display: 'flex',
    gap: '0.75rem',
    marginBottom: '1.5rem',
  },
  badge: {
    background: 'rgba(99, 102, 241, 0.1)',
    border: '1px solid rgba(99, 102, 241, 0.3)',
    color: '#A5B4FC',
    padding: '0.35rem 0.85rem',
    borderRadius: '100px',
    fontSize: '0.85rem',
    fontWeight: 600,
    letterSpacing: '0.5px',
  },
  badgeRailway: {
    background: 'rgba(236, 72, 153, 0.1)',
    border: '1px solid rgba(236, 72, 153, 0.3)',
    color: '#F472B6',
    padding: '0.35rem 0.85rem',
    borderRadius: '100px',
    fontSize: '0.85rem',
    fontWeight: 600,
    letterSpacing: '0.5px',
  },
  title: {
    fontSize: '2.5rem',
    fontWeight: 800,
    lineHeight: 1.2,
    margin: '0 0 1rem 0',
    letterSpacing: '-0.5px',
  },
  gradientText: {
    background: 'linear-gradient(135deg, #818CF8 0%, #22D3EE 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
  },
  subtitle: {
    fontSize: '1.1rem',
    lineHeight: '1.6',
    color: '#9CA3AF',
    margin: '0 0 2rem 0',
  },
  statusBox: {
    background: 'rgba(16, 185, 129, 0.05)',
    border: '1px solid rgba(16, 185, 129, 0.2)',
    borderRadius: '16px',
    padding: '1.25rem',
    marginBottom: '2rem',
  },
  statusHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
    marginBottom: '0.5rem',
  },
  statusDot: {
    width: '10px',
    height: '10px',
    backgroundColor: '#10B981',
    borderRadius: '50%',
    display: 'inline-block',
    boxShadow: '0 0 10px #10B981',
  },
  statusText: {
    fontWeight: 600,
    color: '#34D399',
    fontSize: '0.95rem',
  },
  statusDetails: {
    margin: 0,
    fontSize: '0.875rem',
    color: '#9CA3AF',
    lineHeight: '1.4',
  },
  stepsContainer: {
    background: 'rgba(255, 255, 255, 0.02)',
    border: '1px solid rgba(255, 255, 255, 0.04)',
    borderRadius: '16px',
    padding: '1.5rem',
    marginBottom: '1.5rem',
  },
  stepsTitle: {
    margin: '0 0 1rem 0',
    fontSize: '1rem',
    fontWeight: 600,
    color: '#E5E7EB',
  },
  stepsList: {
    margin: 0,
    padding: 0,
    listStyleType: 'none',
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
  },
  stepItem: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '0.75rem',
    fontSize: '0.9rem',
    color: '#9CA3AF',
    lineHeight: '1.4',
  },
  stepNum: {
    background: 'rgba(255, 255, 255, 0.08)',
    width: '24px',
    height: '24px',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: '#E5E7EB',
    fontWeight: 600,
    fontSize: '0.8rem',
    flexShrink: 0,
  },
  footer: {
    textAlign: 'center',
    fontSize: '0.8rem',
    color: '#4B5563',
    marginTop: '1rem',
    borderTop: '1px solid rgba(255, 255, 255, 0.04)',
    paddingTop: '1.25rem',
  }
};
