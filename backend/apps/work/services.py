def get_byline(contributions) -> list[dict]:
    """Return deduplicated agent list for byline rendering."""
    seen = set()
    result = []
    for c in contributions:
        if c.role and c.agent and c.agent.id not in seen:
            seen.add(c.agent.id)
            result.append({"id": c.agent.id, "text": getattr(c, "display_name", "") or c.agent.name})
    return result


def get_credits(contributions) -> list[dict]:
    """Return agents grouped by role for credit rendering."""
    groups = {}
    for c in contributions:
        if c.role and c.agent:
            groups.setdefault(c.role.verb, {}).setdefault(
                c.agent.id, {"id": c.agent.id, "text": getattr(c, "display_name", "") or c.agent.name}
            )

    return [{"role": role, "agents": list(agents.values())} for role, agents in groups.items()]
