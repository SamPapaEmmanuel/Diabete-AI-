import { useState } from 'react';
import type { FormEvent } from 'react';
import {
  ArrowRight,
  Eye,
  EyeOff,
  LockKeyhole,
  Mail,
  ShieldCheck,
} from 'lucide-react';
import { AccountRequestError, accountRequest } from './account_client';
import type { Account } from './account_client';
import { reportCopy as t, responseCopy } from './report_copy';

type AccountMode = 'login' | 'register' | 'forgot' | 'verify' | 'reset';

function initialMode(): AccountMode {
  const action = window.location.hash.split('/')[2]?.split('?')[0];
  return action === 'verify' || action === 'reset' ? action : 'login';
}

export function AccountPanel({
  account,
  loading,
  online,
  onAccountChange,
}: {
  account: Account | null;
  loading: boolean;
  online: boolean;
  onAccountChange: (account: Account | null) => void;
}) {
  const [mode, setMode] = useState<AccountMode>(initialMode);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [visible, setVisible] = useState(false);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const token = new URLSearchParams(
    window.location.hash.split('?')[1] ?? '',
  ).get('token');

  function changeMode(next: AccountMode) {
    setMode(next);
    setError(null);
    setMessage(null);
    setPassword('');
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    setMessage(null);
    try {
      if (mode === 'login') {
        const result = await accountRequest<Account>('/auth/login', {
          email,
          password,
        });
        setPassword('');
        onAccountChange(result);
      } else {
        const path =
          mode === 'register'
            ? '/auth/register'
            : mode === 'forgot'
              ? '/auth/password-reset-requests'
              : mode === 'verify'
                ? '/auth/verify-email'
                : '/auth/password-resets';
        if ((mode === 'verify' || mode === 'reset') && !token)
          throw new AccountRequestError('account.missing_link');
        const body =
          mode === 'register'
            ? { email, password }
            : mode === 'forgot'
              ? { email }
              : mode === 'verify'
                ? { token: token ?? '' }
                : { token: token ?? '', password };
        const result = await accountRequest<{ message_key: string }>(
          path,
          body,
        );
        setMessage(responseCopy(result.message_key));
        setPassword('');
        if (mode === 'reset' || mode === 'verify') {
          window.history.replaceState(null, '', '#/account');
          if (mode === 'reset') onAccountChange(null);
          else if (account)
            onAccountChange(await accountRequest<Account>('/account'));
          setMode('login');
        }
      }
    } catch (failure) {
      setError(
        responseCopy(
          failure instanceof AccountRequestError
            ? failure.messageKey
            : 'account.request_failed',
        ),
      );
      requestAnimationFrame(() =>
        document.getElementById('account-error')?.focus(),
      );
    } finally {
      setBusy(false);
    }
  }

  async function signOut() {
    setBusy(true);
    setError(null);
    try {
      await accountRequest('/auth/logout', {});
      onAccountChange(null);
    } catch {
      setError(t('account.request_failed'));
    } finally {
      setBusy(false);
    }
  }

  async function resend() {
    if (!account) return;
    setBusy(true);
    setError(null);
    try {
      const result = await accountRequest<{ message_key: string }>(
        '/auth/resend-verification',
        { email: account.email },
      );
      setMessage(responseCopy(result.message_key));
    } catch {
      setError(t('account.request_failed'));
    } finally {
      setBusy(false);
    }
  }

  const isLinkAction = mode === 'verify' || mode === 'reset';
  const showAccount = account && !isLinkAction;
  const actionLabel =
    mode === 'login'
      ? 'account.sign_in'
      : mode === 'register'
        ? 'account.register'
        : mode === 'forgot'
          ? 'account.send_reset'
          : mode === 'verify'
            ? 'account.verify_action'
            : 'account.save_password';

  return (
    <>
      <div className="page-heading">
        <p className="eyebrow">{t('account.eyebrow')}</p>
        <h1>{t('account.heading')}</h1>
        <p className="page-intro">{t('account.intro')}</p>
      </div>
      <div className="account-columns">
        <section className="account-panel" aria-busy={busy || loading}>
          {error && (
            <div
              className="form-error"
              id="account-error"
              tabIndex={-1}
              role="alert"
            >
              <h2>{t('account.error_heading')}</h2>
              <p>{error}</p>
            </div>
          )}
          {message && (
            <p className="form-message" role="status">
              {message}
            </p>
          )}
          {loading ? (
            <p role="status">{t('account.busy')}</p>
          ) : showAccount ? (
            <>
              <span className="section-icon">
                <UserIdentity verified={account.verified} />
              </span>
              <h2 className="account-email">{account.email}</h2>
              <p className="account-verification">
                {t(
                  account.verified ? 'account.verified' : 'account.unverified',
                )}
              </p>
              <p>
                {t(
                  account.verified
                    ? 'account.ready_body'
                    : 'account.verification_body',
                )}
              </p>
              {!account.verified && (
                <button
                  className="primary-button"
                  onClick={() => void resend()}
                  disabled={busy || !online}
                >
                  {t('account.resend')}
                </button>
              )}
              <button
                className="secondary-button"
                onClick={() => void signOut()}
                disabled={busy || !online}
              >
                {t('account.sign_out')}
              </button>
            </>
          ) : (
            <>
              {(mode === 'login' || mode === 'register') && (
                <div className="account-tabs">
                  <button
                    type="button"
                    className={mode === 'login' ? 'active' : ''}
                    onClick={() => changeMode('login')}
                    aria-pressed={mode === 'login'}
                  >
                    {t('account.sign_in')}
                  </button>
                  <button
                    type="button"
                    className={mode === 'register' ? 'active' : ''}
                    onClick={() => changeMode('register')}
                    aria-pressed={mode === 'register'}
                  >
                    {t('account.register')}
                  </button>
                </div>
              )}
              {mode === 'forgot' && <h2>{t('account.reset_heading')}</h2>}
              {mode === 'verify' && <h2>{t('account.verify_heading')}</h2>}
              {mode === 'reset' && <h2>{t('account.reset_heading')}</h2>}
              <form onSubmit={(event) => void submit(event)}>
                {(mode === 'login' ||
                  mode === 'register' ||
                  mode === 'forgot') && (
                  <label className="form-field" htmlFor="account-email">
                    <span>{t('account.email')}</span>
                    <input
                      id="account-email"
                      type="email"
                      autoComplete="email"
                      value={email}
                      required
                      maxLength={320}
                      onChange={(event) => setEmail(event.target.value)}
                    />
                  </label>
                )}
                {(mode === 'login' ||
                  mode === 'register' ||
                  mode === 'reset') && (
                  <div className="form-field">
                    <label htmlFor="account-password">
                      {t(
                        mode === 'reset'
                          ? 'account.new_password'
                          : 'account.password',
                      )}
                    </label>
                    <span className="password-field">
                      <input
                        id="account-password"
                        type={visible ? 'text' : 'password'}
                        autoComplete={
                          mode === 'login' ? 'current-password' : 'new-password'
                        }
                        value={password}
                        minLength={15}
                        maxLength={128}
                        required
                        aria-describedby="password-hint"
                        onChange={(event) => setPassword(event.target.value)}
                      />
                      <button
                        type="button"
                        className="password-toggle"
                        onClick={() => setVisible(!visible)}
                        aria-label={t(
                          visible
                            ? 'account.hide_password'
                            : 'account.show_password',
                        )}
                      >
                        {visible ? (
                          <EyeOff
                            size={18}
                            strokeWidth={2}
                            aria-hidden="true"
                          />
                        ) : (
                          <Eye size={18} strokeWidth={2} aria-hidden="true" />
                        )}
                      </button>
                    </span>
                    <span id="password-hint" className="small-copy">
                      {t('account.password_hint')}
                    </span>
                  </div>
                )}
                {mode === 'verify' && !token && (
                  <p role="alert">{t('account.missing_link')}</p>
                )}
                {!online && <p role="status">{t('account.offline')}</p>}
                <button
                  className="primary-button account-submit"
                  type="submit"
                  disabled={busy || !online || (isLinkAction && !token)}
                >
                  {t(busy ? 'account.busy' : actionLabel)}
                  <ArrowRight size={18} strokeWidth={2} aria-hidden="true" />
                </button>
                {mode === 'login' ? (
                  <button
                    className="text-button"
                    type="button"
                    onClick={() => changeMode('forgot')}
                  >
                    {t('account.forgot')}
                  </button>
                ) : (
                  mode !== 'register' && (
                    <button
                      className="text-button"
                      type="button"
                      onClick={() => changeMode('login')}
                    >
                      {t('account.back')}
                    </button>
                  )
                )}
              </form>
            </>
          )}
        </section>
        <aside className="account-assurance">
          <ShieldCheck size={24} strokeWidth={2} aria-hidden="true" />
          <h2>{t('report.privacy_heading')}</h2>
          <p>{t('report.privacy_body')}</p>
          <p className="assurance-detail">
            <LockKeyhole size={18} strokeWidth={2} aria-hidden="true" />
            {t('account.scope')}
          </p>
          <p className="assurance-detail">
            <Mail size={18} strokeWidth={2} aria-hidden="true" />
            {t('account.privacy')}
          </p>
        </aside>
      </div>
    </>
  );
}

function UserIdentity({ verified }: { verified: boolean }) {
  return verified ? (
    <ShieldCheck size={24} strokeWidth={2} aria-hidden="true" />
  ) : (
    <Mail size={24} strokeWidth={2} aria-hidden="true" />
  );
}
