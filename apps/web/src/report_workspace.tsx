import { useCallback, useEffect, useState } from 'react';
import {
  ArrowRight,
  Check,
  ChevronRight,
  CircleHelp,
  FileCheck2,
  FileText,
  History,
  LockKeyhole,
  Moon,
  ShieldCheck,
  Sun,
  Upload,
  UserRound,
  WifiOff,
} from 'lucide-react';
import { AccountPanel } from './account_panel';
import { accountRequest } from './account_client';
import type { Account } from './account_client';
import { reportCopy as t } from './report_copy';
import type { MessageKey } from './report_copy';

type Route = 'report' | 'history' | 'account';
type Theme = 'system' | 'light' | 'dark';
type Connection = 'loading' | 'ready' | 'error';
const destinations = [
  { route: 'report', label: 'nav.report', icon: FileText },
  { route: 'history', label: 'nav.history', icon: History },
  { route: 'account', label: 'nav.account', icon: UserRound },
] as const;

function currentRoute(location: string): Route {
  const name = location.split('/')[1]?.split('?')[0];
  return name === 'history' || name === 'account' ? name : 'report';
}

function preferredTheme(): Theme {
  try {
    const stored = localStorage.getItem('report-theme');
    return stored === 'light' || stored === 'dark' ? stored : 'system';
  } catch {
    return 'system';
  }
}

export function ReportWorkspace() {
  const [location, setLocation] = useState(() => window.location.hash);
  const route = currentRoute(location);
  const [theme, setTheme] = useState<Theme>(preferredTheme);
  const [online, setOnline] = useState(navigator.onLine);
  const [connection, setConnection] = useState<Connection>('loading');
  const [account, setAccount] = useState<Account | null>(null);
  const [accountLoading, setAccountLoading] = useState(true);

  const connect = useCallback((signal?: AbortSignal) => {
    return fetch('/api/v1/health/ready', {
      cache: 'no-store',
      signal: signal
        ? AbortSignal.any([signal, AbortSignal.timeout(10_000)])
        : AbortSignal.timeout(10_000),
    }).then(
      (response) => {
        if (!signal?.aborted) setConnection(response.ok ? 'ready' : 'error');
      },
      () => {
        if (!signal?.aborted) setConnection('error');
      },
    );
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    void connect(controller.signal);
    return () => controller.abort();
  }, [connect]);

  useEffect(() => {
    let active = true;
    void accountRequest<Account>('/account').then(
      (result) => {
        if (active) {
          setAccount(result);
          setAccountLoading(false);
        }
      },
      () => {
        if (active) setAccountLoading(false);
      },
    );
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    const navigate = () => {
      setLocation(window.location.hash);
      document.querySelector<HTMLElement>('#main-content')?.focus();
    };
    const markOnline = () => {
      setOnline(true);
      void connect();
    };
    const markOffline = () => setOnline(false);
    window.addEventListener('hashchange', navigate);
    window.addEventListener('online', markOnline);
    window.addEventListener('offline', markOffline);
    return () => {
      window.removeEventListener('hashchange', navigate);
      window.removeEventListener('online', markOnline);
      window.removeEventListener('offline', markOffline);
    };
  }, [connect]);

  useEffect(() => {
    const media = window.matchMedia('(prefers-color-scheme: dark)');
    const applyTheme = () => {
      document.documentElement.dataset.theme =
        theme === 'system' ? (media.matches ? 'dark' : 'light') : theme;
    };
    applyTheme();
    media.addEventListener('change', applyTheme);
    try {
      localStorage.setItem('report-theme', theme);
    } catch {
      /* A theme can work without storage. */
    }
    return () => media.removeEventListener('change', applyTheme);
  }, [theme]);

  const connectionKey: MessageKey = !online
    ? 'connection.offline'
    : connection === 'ready'
      ? 'connection.ready'
      : connection === 'loading'
        ? 'connection.loading'
        : 'connection.error';

  return (
    <div className="application-shell">
      <a
        className="skip-link"
        href="#main-content"
        onClick={(event) => {
          event.preventDefault();
          document.getElementById('main-content')?.focus();
        }}
      >
        {t('app.skip')}
      </a>
      <aside className="navigation-rail">
        <a className="brand" href="#/report" aria-label={t('app.title')}>
          <span className="brand-mark">
            <FileCheck2 size={24} strokeWidth={2} aria-hidden="true" />
          </span>
          <span>
            <strong>{t('app.brand')}</strong>
            <span>{t('app.brand_detail')}</span>
          </span>
        </a>
        <nav aria-label={t('app.navigation')}>
          {destinations.map(({ route: destination, label, icon: Icon }) => (
            <a
              key={destination}
              href={`#/${destination}`}
              aria-current={route === destination ? 'page' : undefined}
            >
              <Icon size={20} strokeWidth={2} aria-hidden="true" />
              <span>{t(label)}</span>
              <ChevronRight
                className="navigation-chevron"
                size={16}
                strokeWidth={2}
                aria-hidden="true"
              />
            </a>
          ))}
        </nav>
        <div className="rail-note">
          <ShieldCheck size={20} strokeWidth={2} aria-hidden="true" />
          <p>{t('app.disclaimer')}</p>
        </div>
      </aside>
      <div className="workspace-body">
        <header className="workspace-toolbar">
          <p className="breadcrumb">
            {t('app.workspace')}
            <ChevronRight size={16} strokeWidth={2} aria-hidden="true" />
            <span>{t(`nav.${route}`)}</span>
          </p>
          <div className="toolbar-controls">
            <span
              className="connection-indicator"
              role="status"
              aria-live="polite"
            >
              {!online ? (
                <WifiOff size={16} strokeWidth={2} aria-hidden="true" />
              ) : (
                <span className={`connection-dot ${connection}`} />
              )}
              <span>{t(connectionKey)}</span>
            </span>
            <label className="theme-picker">
              {theme === 'dark' ? (
                <Moon size={18} strokeWidth={2} aria-hidden="true" />
              ) : (
                <Sun size={18} strokeWidth={2} aria-hidden="true" />
              )}
              <span className="visually-hidden">{t('theme.label')}</span>
              <select
                value={theme}
                onChange={(event) => setTheme(event.target.value as Theme)}
              >
                <option value="system">{t('theme.system')}</option>
                <option value="light">{t('theme.light')}</option>
                <option value="dark">{t('theme.dark')}</option>
              </select>
            </label>
          </div>
        </header>
        <main id="main-content" tabIndex={-1}>
          {(!online || connection === 'error') && (
            <div className="connection-notice" role="status">
              <WifiOff size={20} strokeWidth={2} aria-hidden="true" />
              <p>{t(connectionKey)}</p>
              {online && (
                <button className="text-button" onClick={() => void connect()}>
                  {t('connection.retry')}
                </button>
              )}
            </div>
          )}
          {route === 'report' && <ReportStart />}
          {route === 'history' && (
            <ReportHistory account={account} loading={accountLoading} />
          )}
          {route === 'account' && (
            <AccountPanel
              key={location}
              account={account}
              loading={accountLoading}
              online={online}
              onAccountChange={setAccount}
            />
          )}
        </main>
        <footer className="workspace-footer">
          <span>{t('app.footer')}</span>
          <span>{t('app.ghana')}</span>
        </footer>
      </div>
    </div>
  );
}

function ReportStart() {
  return (
    <>
      <div className="page-heading">
        <p className="eyebrow">{t('report.eyebrow')}</p>
        <h1>{t('report.heading')}</h1>
        <p className="page-intro">{t('report.intro')}</p>
      </div>
      <div className="report-columns">
        <section className="report-entry" aria-labelledby="report-start-title">
          <span className="section-icon">
            <Upload size={24} strokeWidth={2} aria-hidden="true" />
          </span>
          <h2 id="report-start-title">{t('report.section')}</h2>
          <p>{t('report.description')}</p>
          <div className="report-upload-control">
            <button
              className="primary-button"
              disabled
              aria-describedby="upload-unavailable"
            >
              <Upload size={18} strokeWidth={2} aria-hidden="true" />
              {t('report.upload')}
            </button>
            <p id="upload-unavailable" className="small-copy">
              {t('report.unavailable')}
            </p>
          </div>
          <div className="format-detail">
            <FileText size={18} strokeWidth={2} aria-hidden="true" />
            <div>
              <span>{t('report.formats')}</span>
              <span className="small-copy">{t('report.limits')}</span>
            </div>
          </div>
        </section>
        <section
          className="report-preview"
          aria-labelledby="report-preview-title"
        >
          <div className="preview-caption">
            <span className="eyebrow">{t('report.preview_label')}</span>
            <LockKeyhole size={16} strokeWidth={2} aria-hidden="true" />
          </div>
          <div className="preview-empty">
            <FileText size={32} strokeWidth={2} aria-hidden="true" />
            <h2 id="report-preview-title">{t('report.preview_heading')}</h2>
            <p>{t('report.preview_body')}</p>
          </div>
          <div className="preview-footnote">
            <Check size={16} strokeWidth={2} aria-hidden="true" />
            <span>{t('report.step_two_title')}</span>
          </div>
        </section>
      </div>
      <section className="review-steps" aria-labelledby="review-steps-title">
        <h2 id="review-steps-title">{t('report.steps_heading')}</h2>
        <ol>
          {(['one', 'two', 'three'] as const).map((step, index) => (
            <li key={step}>
              <span className="step-number">
                {String(index + 1).padStart(2, '0')}
              </span>
              <div>
                <h3>{t(`report.step_${step}_title`)}</h3>
                <p>{t(`report.step_${step}_body`)}</p>
              </div>
            </li>
          ))}
        </ol>
      </section>
      <section className="privacy-note" aria-labelledby="privacy-title">
        <ShieldCheck size={24} strokeWidth={2} aria-hidden="true" />
        <div>
          <h2 id="privacy-title">{t('report.privacy_heading')}</h2>
          <p>{t('report.privacy_body')}</p>
        </div>
        <a className="text-link" href="#/account">
          {t('report.account_action')}
          <ArrowRight size={18} strokeWidth={2} aria-hidden="true" />
        </a>
      </section>
    </>
  );
}

function ReportHistory({
  account,
  loading,
}: {
  account: Account | null;
  loading: boolean;
}) {
  return (
    <>
      <div className="page-heading">
        <p className="eyebrow">{t('history.eyebrow')}</p>
        <h1>{t('history.heading')}</h1>
        <p className="page-intro">{t('history.intro')}</p>
      </div>
      <section className="empty-panel">
        <History size={32} strokeWidth={2} aria-hidden="true" />
        {loading ? (
          <p role="status">{t('account.busy')}</p>
        ) : (
          <>
            <h2>
              {t(account ? 'history.empty_heading' : 'history.guest_heading')}
            </h2>
            <p>{t(account ? 'history.empty_body' : 'history.guest_body')}</p>
            {!account && (
              <a href="#/account" className="primary-button">
                {t('history.account_action')}
                <ArrowRight size={18} strokeWidth={2} aria-hidden="true" />
              </a>
            )}
          </>
        )}
      </section>
      <p className="scope-note">
        <CircleHelp size={18} strokeWidth={2} aria-hidden="true" />
        {t('app.disclaimer')}
      </p>
    </>
  );
}
