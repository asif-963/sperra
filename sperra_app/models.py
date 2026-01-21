from django.db import models
from PIL import Image, ImageOps
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify


# --------- Blogs ---------
class Blog(models.Model):
    image = models.ImageField(upload_to="blogs/", help_text="Blog cover image")
    slug = models.SlugField(unique=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while Blog.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)


# ---------Team-------------
class TeamMember(models.Model):
    name = models.CharField(max_length=100, help_text="Full name of the team member")
    profession = models.CharField(
        max_length=100, help_text="Role or profession (e.g. Software Engineer)"
    )
    image = models.ImageField(
        upload_to="team/", blank=True, null=True, help_text="Profile picture"
    )

    # Social links
    linkedin = models.URLField(max_length=200, blank=True, null=True)
    facebook = models.URLField(max_length=200, blank=True, null=True)
    instagram = models.URLField(max_length=200, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Tell base model which images to optimize
    image_fields = ["image"]

    class Meta:
        ordering = ["name"]
        verbose_name = "Team Member"
        verbose_name_plural = "Team Members"

    def __str__(self):
        return f"{self.name} - {self.profession}"

# ----------Testimonial---------------
class Testimonial(models.Model):
    name = models.CharField(
        max_length=100, help_text="Name of the person giving the testimonial"
    )
    image = models.ImageField(
        upload_to="testimonials/", blank=True, null=True, help_text="Profile picture"
    )
    review = models.TextField(help_text="Customer or client review")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    image_fields = ["image"]

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"

    def __str__(self):
        return self.name


#---------Gallery-----------

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class GalleryImage(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="images"
    )
    title = models.CharField(max_length=150, blank=True, null=True)
    image = models.ImageField(upload_to="gallery/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # Tell base model which images to optimize
    image_fields = ["image"]

    def __str__(self):
        return self.title if self.title else f"Image {self.id}"


# --------- Treatments ---------
class Treatments(models.Model):
    image = models.ImageField(upload_to="treatments/", help_text="Treatment cover image")
    slug = models.SlugField(unique=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while Treatments.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)
        
# --------- Treatment FAQs ---------
class TreatmentFAQ(models.Model):
    treatment = models.ForeignKey(
        Treatments,
        on_delete=models.CASCADE,
        related_name="faqs"
    )
    question = models.CharField(max_length=255)
    answer = models.TextField()

    def __str__(self):
        return self.question


#----------ContactMessage------------------------
class ContactMessage(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.phone}"

#---------------Appointments-------------------
class Appointment(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)

    treatment = models.ForeignKey(
        Treatments,
        on_delete=models.CASCADE,
        related_name="appointments"
    )

    appointment_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} - {self.treatment.title}"
