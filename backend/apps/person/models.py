from django.db import models

from apps.core.models import TimeStampedModel


class Person(TimeStampedModel):
    """
    Represents a real-world person such as an author, translator, or editor.

    Roles (e.g., 'Author of Work A', 'Translator of Work B') should be defined
    in a separate intermediate model (e.g., WorkPerson) to allow one person
    to have multiple roles across different works.
    """

    name = models.CharField(max_length=255, verbose_name="姓名")
    bio = models.TextField(blank=True, verbose_name="簡歷")

    class Meta:
        ordering = ["name"]
        verbose_name = "人物"
        verbose_name_plural = "人物"

    def __str__(self):
        return self.name


class PersonAlias(models.Model):
    """
    Stores alternative names, pen names, or localized names for a Person.
    A One-to-Many relationship allows for an unlimited number of aliases.
    """

    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="aliases",
        verbose_name="人物",
    )
    name = models.CharField(max_length=255, verbose_name="別名")

    class Meta:
        ordering = ["name"]
        verbose_name = "人物別名"
        verbose_name_plural = "人物別名"
        unique_together = [["person", "name"]]  # Prevent duplicate aliases for the same person

    def __str__(self):
        return f"{self.name} ({self.person.name})"


class PersonLink(models.Model):
    """
    Stores external links related to a Person, such as Wikipedia pages,
    personal websites, or social media profiles.
    """

    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="links", verbose_name="人物")
    title = models.CharField(max_length=100, help_text="e.g., Personal Website, Wikipedia", verbose_name="連結標題")
    url = models.URLField(max_length=500, verbose_name="網址")

    class Meta:
        ordering = ["title"]
        verbose_name = "人物連結"
        verbose_name_plural = "人物連結"

    def __str__(self):
        return f"{self.title} - {self.person.name}"
