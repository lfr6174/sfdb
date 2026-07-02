import { computed, ref, type WritableComputedRef } from 'vue'
import { useRoute, useRouter, type LocationQuery } from 'vue-router'

/**
 * useUrlFilters — the URL query string as the single source of truth for
 * filter state.
 *
 * Each schema key becomes a writable computed: reading parses the current
 * route query, writing patches it via router.replace. There is no local
 * copy of the state, so URL and UI can never drift apart, and back/forward
 * navigation restores filters for free.
 *
 * Intended for one instance per route view; two instances writing the same
 * params on one page would race each other.
 */

export interface FilterSpec {
  /** How the value is (de)serialized in the URL. */
  type: 'string' | 'csv' | 'number'
  /** Value used when the param is absent; matching values are removed from the URL. */
  default?: string | number | string[]
  /** Set false for params that toParams() should not send to the API
   *  (display-only labels, or params another layer already handles). */
  api?: boolean
}

/** csv → string[], number → number ('' when empty and no default), string → string */
type SpecValue<S extends FilterSpec> = S['type'] extends 'csv'
  ? string[]
  : S['type'] extends 'number'
    ? S['default'] extends number
      ? number
      : number | ''
    : string

export type UrlFilterValues<S extends Record<string, FilterSpec>> = {
  [K in keyof S]: WritableComputedRef<SpecValue<S[K]>>
}

const serialize = (spec: FilterSpec, value: unknown): string | null => {
  if (spec.type === 'csv') return (value as string[]).join(',') || null
  if (value === '' || value == null) return null
  return String(value)
}

const defaultRaw = (spec: FilterSpec): string | null =>
  spec.default == null ? null : serialize(spec, spec.default)

const deserialize = (spec: FilterSpec, raw: string | null) => {
  if (spec.type === 'csv') return raw ? raw.split(',') : []
  if (spec.type === 'number') return raw == null || raw === '' ? '' : Number(raw)
  return raw ?? ''
}

export function useUrlFilters<S extends Record<string, FilterSpec>>(schema: S) {
  const route = useRoute()
  const router = useRouter()

  // Writes queued for the current tick. router.replace is async, so writing
  // params one at a time would let each write start from a stale route.query
  // and clobber the previous one; instead all writes merge here and flush as
  // a single navigation. Reads overlay `pending` on top of route.query so
  // state is consistent even before the flush lands. (null = remove param.)
  const pending = ref<Record<string, string | null> | null>(null)
  let flushing = false

  const flush = async () => {
    if (flushing) return
    flushing = true
    try {
      while (pending.value) {
        const patch = pending.value
        const query: LocationQuery = { ...route.query }
        for (const [key, raw] of Object.entries(patch)) {
          if (raw == null) delete query[key]
          else query[key] = raw
        }
        // Keep the patch in `pending` while the navigation is in flight:
        // reads must keep seeing the new values during the async gap, or
        // watchers observe a phantom flip back to the old URL state.
        await router.replace({ query })
        // Drop what we just flushed — unless a key was re-written meanwhile,
        // in which case the loop flushes it again.
        const rest = Object.entries(pending.value ?? {}).filter(
          ([key, raw]) => !(key in patch) || raw !== patch[key],
        )
        pending.value = rest.length ? Object.fromEntries(rest) : null
      }
    } finally {
      flushing = false
    }
  }

  const write = (patch: Record<string, string | null>) => {
    pending.value = { ...(pending.value ?? {}), ...patch }
    void Promise.resolve().then(flush)
  }

  const readRaw = (key: string): string | null => {
    const p = pending.value
    if (p && key in p) return p[key]
    const v = route.query[key]
    if (Array.isArray(v)) return typeof v[0] === 'string' ? v[0] : null
    return typeof v === 'string' ? v : null
  }

  const values = Object.fromEntries(
    Object.entries(schema).map(([key, spec]) => [
      key,
      computed({
        get: () => deserialize(spec, readRaw(key) ?? defaultRaw(spec)),
        set: (value: string | string[] | number) => {
          const raw = serialize(spec, value)
          write({ [key]: raw === defaultRaw(spec) ? null : raw })
        },
      }),
    ]),
  ) as UrlFilterValues<S>

  /** Query params for the API: every active (non-empty, non-default) filter with api !== false. */
  const toParams = () => {
    const params: Record<string, string> = {}
    for (const [key, spec] of Object.entries(schema)) {
      if (spec.api === false) continue
      const raw = readRaw(key)
      if (raw != null && raw !== '' && raw !== defaultRaw(spec)) params[key] = raw
    }
    return params
  }

  /** Reset the given keys (all schema keys when omitted) to their defaults. */
  const clear = (...keys: (keyof S & string)[]) => {
    const target = keys.length ? keys : Object.keys(schema)
    write(Object.fromEntries(target.map((key) => [key, null])))
  }

  return { values, toParams, clear }
}
