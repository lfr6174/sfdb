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

    name = models.CharField(
        max_length=255, verbose_name="名稱", help_text="人物的真實姓名、最廣為人知的筆名，或組織的正式名稱。"
    )
    agent_type = models.CharField(
        max_length=20,
        choices=AgentType.choices,
        default=AgentType.PERSON,
        verbose_name="類別",
        help_text="區分此為單一人物或是一個組織/團體。",
    )
    about = models.TextField(
        blank=True, verbose_name="簡介", help_text="關於此人物或組織的生平、經歷與背景介紹。可留空。"
    )

    class Meta:
        verbose_name = "人物/組織"
        verbose_name_plural = "人物/組織"
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
        verbose_name="人物/組織",
    )
    name = models.CharField(
        max_length=255,
        verbose_name="別名",
        help_text="此人物/組織使用的其他名稱，例如不同的筆名、本名、外文原名或各種譯名。",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "人物/組織別名"
        verbose_name_plural = "人物/組織別名"
        unique_together = [["agent", "name"]]

    def __str__(self):
        return f"{self.name} ({self.agent.name})"


class AgentLink(models.Model):
    """
    External links for a person or organization, such as Wikipedia pages,
    official websites, or social media profiles.
    """

    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name="links", verbose_name="人物/組織")
    label = models.CharField(
        max_length=100,
        verbose_name="連結標籤",
        help_text="顯示在網頁上的連結文字，例如「個人網站」、「維基百科」、「Twitter (X)」。",
    )
    url = models.URLField(max_length=500, verbose_name="網址", help_text="完整的網址，請包含 https:// 開頭。")

    class Meta:
        ordering = ["label"]
        verbose_name = "人物/組織連結"
        verbose_name_plural = "人物/組織連結"

    def __str__(self):
        return f"{self.label}: {self.agent.name}"
