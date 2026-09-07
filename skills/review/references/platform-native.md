# What the platform already does

The `stdlib:` and `native:` rungs, as a lookup. Reach for the row before the package; install the package only when the native answer is measurably insufficient here (old runtime, an edge case it does not handle, ergonomics that matter at scale).

## Browser
| Reaching for | The platform has |
|---|---|
| date, time, color, range picker | `<input type="date|time|color|range">` |
| modal, accordion, progress, meter | `<dialog>` + `showModal()`, `<details>`, `<progress>`, `<meter>` |
| searchable dropdown, auto-growing textarea | `<datalist>`, `field-sizing: content` |
| sticky header, smooth scroll, snap carousel | `position: sticky`, `scroll-behavior`, `scroll-snap-type` |
| responsive type and spacing | `clamp()`, `@container`, `repeat(auto-fill, minmax())` |
| dark mode, reduced motion | `prefers-color-scheme`, `prefers-reduced-motion` |
| truncation, aspect ratio, nesting, parent selector | `text-overflow`, `-webkit-line-clamp`, `aspect-ratio`, native nesting, `:has()` |
| query-string, deep clone, group-by, uuid | `URLSearchParams`, `structuredClone`, `Object.groupBy`, `crypto.randomUUID()` |
| number, date, relative-time, plural formatting | `Intl.NumberFormat`, `Intl.DateTimeFormat`, `Intl.RelativeTimeFormat`, `Intl.PluralRules` |
| clipboard, share, online check, timeout | `navigator.clipboard`, `navigator.share`, `navigator.onLine`, `AbortSignal.timeout()` |
| infinite scroll, resize, mutation watchers | `IntersectionObserver`, `ResizeObserver`, `MutationObserver` |
| event bus, small persistence | `EventTarget` + `CustomEvent`, `localStorage` |
| debounce | `let t; const debounce = (fn, ms) => (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); };` |

## Node
| Reaching for | Node has |
|---|---|
| mkdirp, rimraf, path-exists | `fs.mkdirSync(p, {recursive: true})`, `fs.rmSync(p, {recursive: true, force: true})`, `fs.existsSync` |
| uuid, array-uniq, array-flatten, object-assign | `crypto.randomUUID()`, `[...new Set(a)]`, `a.flat(Infinity)`, spread |
| load-json-file, write-json-file | `JSON.parse(fs.readFileSync(p, "utf8"))`, `fs.writeFileSync(p, JSON.stringify(o, null, 2))` |
| is-stream, pkg-dir | `x instanceof stream.Readable`, `import.meta.dirname` |

## Python
| Reaching for | Python has |
|---|---|
| dateutil (basic), pytz | `datetime.fromisoformat`, `zoneinfo.ZoneInfo` |
| attrs (simple), six, pathlib2, enum34 | `@dataclass`, nothing, `pathlib`, `enum` |
| requests (one GET), click (one command) | `urllib.request`, `argparse` |
| mergedeep, more-itertools (basic), toolz (basic) | `a \| b`, `itertools`, `functools` |
| simplejson, tabulate (debug) | `json`, `pprint` |

## Swift
| Reaching for | The platform has |
|---|---|
| date, color, photo pickers; search; refresh; swipe actions | `DatePicker`, `ColorPicker`, `PhotosPicker`, `.searchable`, `.refreshable`, `.swipeActions` |
| async image, charts, markdown, share, spinner, maps, grids | `AsyncImage`, Swift Charts, `AttributedString(markdown:)`, `ShareLink`, `ProgressView`, `Map`, `LazyVGrid` |
| JSON, HTTP, formatting, regex, crypto, keychain, persistence, logging | `Codable`, `URLSession`, `.formatted()`, `Regex`, `CryptoKit`, `SecItem`, `SwiftData`, `Logger` |

## Database
| Reaching for app code | The database has |
|---|---|
| pagination, running totals, rank in group, pivot | `LIMIT/OFFSET`, `SUM() OVER`, `RANK() OVER (PARTITION BY)`, `FILTER (WHERE)` |
| dedupe, tree traversal, basic search, JSON | `DISTINCT` / `ON CONFLICT DO NOTHING`, `WITH RECURSIVE`, `tsvector` / FTS5, `jsonb` / `JSON_EXTRACT` |
| uuid, timestamps, uniqueness, integrity, ranges | `gen_random_uuid()`, `DEFAULT now()`, `UNIQUE`, `FOREIGN KEY`, `CHECK` |

The pattern: the platform team spent years on the problem, someone wrapped it, the wrapper goes unmaintained, you debug the wrapper. Skip the wrapper.

Distilled from DietrichGebert/ponytail `docs/platform-native.md`.
