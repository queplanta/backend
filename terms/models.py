


class Term(DocumentBase):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=512)

    description = models.TextField(null=True, blank=True)

    wikipedia_url = models.URLField(null=True)

    def save(self, *args, **kwargs):
        if not self.slug or len(self.slug) == 0:
            self.slug = slugify(self.title)
        return super(Term, self).save(*args, **kwargs)
