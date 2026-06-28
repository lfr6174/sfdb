import { watchEffect, type MaybeRefOrGetter, toValue } from 'vue'

export function useDocumentMeta(
  title: MaybeRefOrGetter<string | null | undefined>,
  description?: MaybeRefOrGetter<string | null | undefined>,
) {
  watchEffect(() => {
    const t = toValue(title)
    if (t) {
      document.title = `${t} | 臺灣科幻概念資料庫`
    } else {
      document.title = '臺灣科幻概念資料庫'
    }

    if (description !== undefined) {
      const desc = toValue(description)
      if (desc) {
        let el = document.querySelector('meta[name="description"]')
        if (!el) {
          el = document.createElement('meta')
          el.setAttribute('name', 'description')
          document.head.appendChild(el)
        }
        el.setAttribute('content', desc)
      }
    }
  })
}
