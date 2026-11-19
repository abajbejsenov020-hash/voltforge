import { BuildFileError, readBuildFile } from '../services/build-file.js';

export const ACCOUNT_CHANGE_KEY = 'voltmodd-account-change';

const accountViews = {
  login: {
    heading: 'Log in',
    description: 'Open your private garage and sync builds across devices.',
    submit: 'Log in',
  },
  signup: {
    heading: 'Sign up',
    description: 'Create an account with a password of at least 12 characters.',
    submit: 'Create account',
  },
  reset: {
    heading: 'Reset password',
    description: 'Enter the email address you use for VOLTMODD.',
    submit: 'Send reset link',
  },
  password: {
    heading: 'Choose a new password',
    description: 'Use at least 12 characters.',
    submit: 'Save new password',
  },
  account: { heading: 'Your account' },
};

export async function loadAccountSession(api) {
  try {
    const session = await api.accountSession();
    return typeof session.enabled === 'boolean' ? session : null;
  } catch (error) {
    // Earlier local servers do not have an account session route.
    return error.status === 404 ? { enabled: false, user: null } : null;
  }
}

export function bindAccount({ api, session, readDrafts, onImport }) {
  if (!session?.enabled) return;
  const byId = (id) => document.getElementById(id);
  const dialog = byId('accountDialog');
  const form = byId('accountForm');
  const heading = byId('accountHeading');
  const description = byId('accountDescription');
  const email = byId('accountEmail');
  const password = byId('accountPassword');
  const submit = byId('submitAccount');
  const message = byId('accountStatus');
  const toggleButtons = {
    login: byId('showLogin'),
    signup: byId('showSignup'),
    reset: byId('showReset'),
  };
  const importButton = byId('importLocalBuilds');
  const importFileButton = byId('importBuildFile');
  const fileInput = byId('garageFile');
  const logout = byId('logOut');
  const close = byId('closeAccount');
  let mode;
  let busy = false;

  function showStatus(text, isError = false) {
    message.textContent = text;
    message.classList.toggle('account-error', isError);
  }

  function show(view, status = '', isError = false) {
    mode = view;
    const spec = accountViews[view];
    const account = view === 'account';
    form.hidden = account;
    email.disabled = account || view === 'password';
    password.disabled = account || view === 'reset';
    byId('accountEmailField').hidden = email.disabled;
    byId('accountPasswordField').hidden = password.disabled;
    email.autocomplete = view === 'reset' ? 'email' : 'username';
    password.autocomplete = view === 'login' ? 'current-password' : 'new-password';
    password.minLength = view === 'signup' || view === 'password' ? 12 : 0;
    password.value = '';
    submit.textContent = spec.submit || '';
    heading.textContent = spec.heading;
    description.textContent = account ? session.user.email : spec.description;
    toggleButtons.login.hidden = account || view === 'login' || view === 'password';
    toggleButtons.signup.hidden = view !== 'login';
    toggleButtons.reset.hidden = view !== 'login';
    importButton.hidden = importFileButton.hidden = logout.hidden = !account;
    importButton.disabled = account && readDrafts().length === 0;
    showStatus(status, isError);
    if (!dialog.open) dialog.showModal();
    (account ? heading : email.disabled ? password : email).focus();
  }

  function reloadForAccountChange() {
    try {
      localStorage.setItem(ACCOUNT_CHANGE_KEY, crypto.randomUUID());
    } catch {
      // The other tabs recheck their session when they regain focus.
    }
    location.reload();
  }

  async function run(operation) {
    if (busy) return;
    busy = true;
    dialog.setAttribute('aria-busy', 'true');
    const actions = [
      close,
      submit,
      importButton,
      importFileButton,
      logout,
      ...Object.values(toggleButtons),
    ].filter((button) => !button.disabled);
    for (const button of actions) button.disabled = true;
    showStatus('');
    try {
      await operation();
    } catch (error) {
      showStatus(
        error.status || error instanceof BuildFileError
          ? error.message
          : 'Could not connect. Please try again.',
        true,
      );
    } finally {
      busy = false;
      dialog.removeAttribute('aria-busy');
      for (const button of actions) button.disabled = false;
    }
  }

  async function importBuilds(builds, note = '') {
    let imported = 0;
    let skipped = 0;
    for (let offset = 0; offset < builds.length; offset += 100) {
      const batch = await api.importBuildsWithResult(builds.slice(offset, offset + 100));
      imported += batch.imported;
      skipped += batch.skipped;
    }
    await onImport();
    showStatus(
      [
        `Imported ${imported} ${imported === 1 ? 'build' : 'builds'}.`,
        skipped && `${skipped} already in your account.`,
        note,
      ]
        .filter(Boolean)
        .join(' '),
    );
  }

  document.body.classList.add('account-enabled');
  for (const id of ['accountBtn', 'setupAccountBtn']) {
    const button = byId(id);
    button.hidden = false;
    button.textContent = session.user ? 'Account' : 'Log in';
    button.addEventListener('click', () =>
      show(session.recovering ? 'password' : session.user ? 'account' : 'login'),
    );
  }
  heading.tabIndex = -1;
  close.addEventListener('click', () => dialog.close());
  dialog.addEventListener('cancel', (event) => {
    if (busy) event.preventDefault();
  });
  dialog.addEventListener('close', () => {
    form.reset();
    showStatus('');
  });
  for (const [view, button] of Object.entries(toggleButtons))
    button.addEventListener('click', () => show(view));

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const address = email.value.trim();
    const secret = password.value;
    void run(async () => {
      if (mode === 'reset') {
        await api.resetPassword(address);
        show('login', 'If that email has an account, open the reset link in this browser.');
      } else if (mode === 'signup') {
        const result = await api.signUp(address, secret);
        if (result.user) reloadForAccountChange();
        else show('login', 'Check your email and open the confirmation link in this browser.');
      } else {
        if (mode === 'password') await api.setPassword(secret);
        else await api.logIn(address, secret);
        reloadForAccountChange();
      }
    });
  });
  logout.addEventListener('click', () => {
    void run(async () => {
      await api.logOut();
      reloadForAccountChange();
    });
  });
  importButton.addEventListener('click', () => {
    void run(() => importBuilds(readDrafts(), 'Your local drafts are still on this device.'));
  });
  importFileButton.addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', () => {
    const file = fileInput.files[0];
    fileInput.value = '';
    if (file) void run(async () => importBuilds(await readBuildFile(file)));
  });

  const url = new URL(location.href);
  const callback = url.searchParams.get('auth');
  if (callback) {
    url.searchParams.delete('auth');
    history.replaceState(history.state, '', url);
  }
  if (session.recovering) show('password');
  else if (callback === 'confirmed') show(session.user ? 'account' : 'login', 'Email confirmed.');
  else if (callback === 'reset' || callback === 'error')
    show(session.user ? 'account' : 'login', 'This email link is invalid or has expired.', true);
}
