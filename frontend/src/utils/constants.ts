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
