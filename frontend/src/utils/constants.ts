// Display order for concept category groups. Labels come from the API's
// category_display (backend ConceptCategory labels are the single source of
// truth); this list only decides ordering. Unknown labels sort last, so a new
// backend category degrades to "shown, at the bottom" instead of crashing.
export const CONCEPT_CATEGORY_ORDER = ['新異 Novum', '敘事 Narrative', '主題 Theme']

/** Sort key for category group labels: known ones in fixed order, unknown last. */
export const categoryOrder = (label: string) => {
  const i = CONCEPT_CATEGORY_ORDER.indexOf(label)
  return i === -1 ? CONCEPT_CATEGORY_ORDER.length : i
}

// Work filter options. NOTE: values and labels mirror the backend TextChoices
// in backend/apps/work/models.py — when a choice changes there, update here.
export const GENRE_OPTIONS = [
  { value: 'novel', label: '小說' },
  { value: 'poem', label: '詩' },
  { value: 'comic', label: '漫畫' },
]
export const LENGTH_OPTIONS = [
  { value: 'long', label: '長篇' },
  { value: 'short', label: '中短篇' },
]
export const PROVENANCE_OPTIONS = [
  { value: 'original', label: '原創' },
  { value: 'licensed', label: '代理' },
]
// Encoding level: `level` drives the ring pictogram (lit segments of 4),
// `description` is the full wording shown in tooltips. Short labels only —
// the backend TextChoices keep the descriptive admin wording.
export const ENCODING_LEVEL_OPTIONS = [
  { value: 'minimal', label: '簡略著錄', level: 1, description: '僅登錄作品名等識別資訊' },
  { value: 'secondary', label: '間接著錄', level: 2, description: '依二手資料著錄' },
  { value: 'partial', label: '部分核校', level: 3, description: '已核對原始資料但部分欄位未填' },
  { value: 'full', label: '完整核校', level: 4, description: '已核對原始資料並填寫全數欄位' },
]
export const LANGUAGE_OPTIONS = [
  { value: 'zh-hant', label: '繁體中文' },
  { value: 'zh-hans', label: '簡體中文' },
  { value: 'en', label: '英文' },
  { value: 'ja', label: '日文' },
  { value: 'other', label: '其他' },
]
