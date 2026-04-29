def build_work_byline(work) -> str:
    """
    建立作品的作者群 (Byline) 顯示字串。
    會過濾重複的人物名稱，若無相關人物則回傳「佚名」。
    """
    credits = work.credits.all()
    if not credits:
        return "佚名"

    # 利用 dict 鍵值不重複且保留插入順序的特性
    return "、".join(dict.fromkeys(c.person.name for c in credits))
