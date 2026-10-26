export interface Account {
  id: string;
  email: string;
  verified: boolean;
  can_save_reports: boolean;
  locale: string;
  theme: string;
}

export class AccountRequestError extends Error {
  constructor(public readonly messageKey: string) {
    super(messageKey);
  }
}

let csrfToken: string | undefined;

export async function accountRequest<T>(
  path: string,
  body?: Record<string, string>,
): Promise<T> {
  if (body && !csrfToken) {
    const csrfResponse = await fetch('/api/v1/auth/csrf', {
      credentials: 'same-origin',
      cache: 'no-store',
      signal: AbortSignal.timeout(10_000),
    });
    if (!csrfResponse.ok) throw new AccountRequestError('service.unavailable');
    const result = (await csrfResponse.json()) as { token: string };
    csrfToken = result.token;
  }
  const response = await fetch(`/api/v1${path}`, {
    method: body ? 'POST' : 'GET',
    credentials: 'same-origin',
    cache: 'no-store',
    signal: AbortSignal.timeout(10_000),
    headers: body
      ? { 'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken ?? '' }
      : {},
    ...(body ? { body: JSON.stringify(body) } : {}),
  });
  if (!response.ok) {
    const error = (await response.json().catch(() => ({}))) as {
      message_key?: string;
    };
    if (error.message_key === 'auth.csrf_invalid') csrfToken = undefined;
    throw new AccountRequestError(error.message_key ?? 'service.unavailable');
  }
  if (['/auth/login', '/auth/logout', '/auth/password-resets'].includes(path))
    csrfToken = undefined;
  return response.status === 204
    ? (undefined as T)
    : ((await response.json()) as T);
}
