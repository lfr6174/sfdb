def build_work_byline(work) -> str:
    """
    建立作品的作者群 (Byline) 顯示字串。
    會過濾重複的人物名稱，若無相關人物則回傳「佚名」。
    """
    credits = work.credits.all()
    if not credits:
        return "佚名"

    seen = set()
    names = []
    for c in credits:
        if c.person.name not in seen:
            seen.add(c.person.name)
            names.append(c.person.name)

    return "、".join(names)
