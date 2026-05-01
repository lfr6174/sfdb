def build_work_byline(work) -> str:
    """
    建立作品的作者群 (Byline) 顯示字串。
    會過濾重複的主體名稱，若無相關主體則回傳「佚名」。
    """
    credits = work.credits.all()
    if not credits:
        return "佚名"

    names = [c.agent.name for c in credits if c.agent]

    if not names:
        return "佚名"

    return "、".join(dict.fromkeys(names))
