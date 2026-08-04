// Contract fixture 15: TypeScript legacy API reference.

export function fetchLegacyConfig(): Promise<{ runtime: string }> {
  return fetch('/api/legacy/config').then((response) => ({
    runtime: response.headers.get('x-runtime') ?? 'legacy',
  }));
}

// legacy_runner dual-path comment marker used by text scanners.