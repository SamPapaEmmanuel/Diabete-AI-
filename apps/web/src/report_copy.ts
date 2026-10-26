import messages from '../../../content/locales/en-GH.json';

export type MessageKey = keyof typeof messages;

export function reportCopy(key: MessageKey): string {
  return messages[key];
}

export function responseCopy(key: string): string {
  return Object.hasOwn(messages, key)
    ? messages[key as MessageKey]
    : messages['account.request_failed'];
}
