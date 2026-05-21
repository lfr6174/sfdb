import { watchEffect, type MaybeRefOrGetter, toValue } from 'vue'

export function useDocumentTitle(title: MaybeRefOrGetter<string | null | undefined>) {
  watchEffect(() => {
    const t = toValue(title)
    if (t) {
      document.title = `${t} | 臺灣科幻概念資料庫`
    } else {
      document.title = '臺灣科幻概念資料庫'
    }
  })
}
