import { writable } from 'svelte/store';

function getInitialTheme() {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme !== null) {
    return savedTheme;
  }
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

export const theme = writable<string>(getInitialTheme());

// Subscribe to theme changes
theme.subscribe((value) => {
  if (typeof document !== 'undefined') {
    document.documentElement.setAttribute('data-theme', value);
  }
});

// Listen for system theme changes
if (typeof window !== 'undefined') {
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (localStorage.getItem('theme') === null) {
      // Only update if user hasn't manually set a theme
      theme.set(e.matches ? 'dark' : 'light');
    }
  });
}
