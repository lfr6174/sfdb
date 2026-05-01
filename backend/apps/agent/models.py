from django.db import models

from apps.core.models import TimeStampedModel


class Agent(TimeStampedModel):
    """
    Entity having a role in a resource, such as a person or organization.
    https://id.loc.gov/ontologies/bibframe.html#Agent
    """

    class AgentType(models.TextChoices):
        PERSON = "person", "個人"
        ORGANIZATION = "organization", "組織"

    name = models.CharField(max_length=255, verbose_name="名稱")
    agent_type = models.CharField(
        max_length=20, choices=AgentType.choices, default=AgentType.PERSON, verbose_name="類別"
    )
    about = models.TextField(blank=True, verbose_name="簡介")

    class Meta:
        verbose_name = "主體"
        verbose_name_plural = "主體"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["agent_type"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_agent_type_display()})"


class AgentAlias(models.Model):
    """
    Other common names for a person or organization, such as pen names
    """

    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name="aliases",
        verbose_name="主體",
    )
    name = models.CharField(max_length=255, verbose_name="別名")

    class Meta:
        ordering = ["name"]
        verbose_name = "主體別名"
        verbose_name_plural = "主體別名"
        unique_together = [["agent", "name"]]

    def __str__(self):
        return f"{self.name} ({self.agent.name})"


class AgentLink(models.Model):
    """
    External links for a person or organization, such as Wikipedia pages,
    official websites, or social media profiles.
    """

    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name="links", verbose_name="主體")
    label = models.CharField(max_length=100, verbose_name="連結標籤")
    url = models.URLField(max_length=500, verbose_name="網址")

    class Meta:
        ordering = ["label"]
        verbose_name = "主體連結"
        verbose_name_plural = "主體連結"

    def __str__(self):
        return f"{self.label}: {self.agent.name}"
