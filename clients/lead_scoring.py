from django.utils import timezone


def calculate_lead_score(lead):
    score = 0
    breakdown = {}

    if lead.email:
        score += 10
        breakdown["has_email"] = 10

    if lead.phone:
        score += 5
        breakdown["has_phone"] = 5

    if lead.company_name:
        score += 5
        breakdown["has_company"] = 5

    if lead.source:
        source = lead.source.lower()
        if source in {"website", "referral", "demo request", "demo_request"}:
            score += 20
            breakdown["high_intent_source"] = 20

    if lead.owner:
        score += 5
        breakdown["assigned_owner"] = 5

    if lead.last_contacted_at:
        days_since_contact = (timezone.now() - lead.last_contacted_at).days
        if days_since_contact <= 3:
            score += 10
            breakdown["recent_contact"] = 10
        elif days_since_contact > 14:
            score -= 5
            breakdown["stale_contact"] = -5

    if lead.next_follow_up_at:
        if lead.next_follow_up_at <= timezone.now():
            score += 10
            breakdown["follow_up_due"] = 10

    if lead.status == lead.Status.QUALIFIED:
        score += 15
        breakdown["qualified_status"] = 15
    elif lead.status == lead.Status.CONTACTED:
        score += 5
        breakdown["contacted_status"] = 5
    elif lead.status == lead.Status.LOST:
        score -= 20
        breakdown["lost_status"] = -20

    if lead.priority == lead.Priority.HIGH:
        score += 10
        breakdown["high_priority"] = 10

    score = max(0, min(score, 100))

    if score >= 70:
        priority = lead.Priority.HIGH
    elif score >= 40:
        priority = lead.Priority.MEDIUM
    else:
        priority = lead.Priority.LOW

    return score, breakdown, priority