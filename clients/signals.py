from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Interaction


@receiver([post_save, post_delete], sender=Interaction)
def update_lead_score_on_interaction_change(sender, instance, **kwargs):
    lead = instance.lead
    if lead:
        lead.recalculate_score(save=True)