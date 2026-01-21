from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models.functions import Lower
from django.db.models.functions import Random
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
import json



from .models import (
    Blog,TeamMember,Testimonial,Category, GalleryImage,
    Treatments,TreatmentFAQ, ContactMessage, Appointment
    
)
from .forms import (
    BlogForm,TeamMemberForm, TestimonialForm, CategoryForm,
    GalleryImageForm,TreatmentsForm, TreatmentFAQFormSet,ContactForm
)











def index(request):
    testimonials = Testimonial.objects.all()
    treatments_qs = Treatments.objects.order_by(Random())[:6]
    blogs = Blog.objects.order_by(Random())[:3]
    treatments = Treatments.objects.all()

    if request.method == "POST":
        Appointment.objects.create(
            first_name=request.POST.get("first_name"),
            last_name=request.POST.get("last_name"),
            phone=request.POST.get("phone"),
            treatment_id=request.POST.get("treatment"),
            appointment_date=request.POST.get("appointment_date"),
        )
        messages.success(request, "Appointment booked successfully!")
        return redirect("index")

    return render(request, 'index.html', {"testimonials": testimonials,"treatments_qs":treatments_qs,"blogs":blogs,"treatments": treatments})

def about(request):
    return render(request, 'about.html')

def our_doctors(request):
    team_members = TeamMember.objects.all()
    return render(request, 'our-doctors.html',{"team_members":team_members})

def treatments(request):
    treatments_qs = Treatments.objects.all()
    paginator = Paginator(treatments_qs, 6)  # 6 per page

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "treatments.html", {
        "page_obj": page_obj
    })

def treatment_details(request,slug):
    treatment = get_object_or_404(Treatments, slug=slug)

    other_treatments = Treatments.objects.exclude(id=treatment.id)

    return render(request, "treatment-details.html", {
        "treatment": treatment,
        "other_treatments": other_treatments,
    })

def blogs(request):
    blogs = Blog.objects.all()
    paginator = Paginator(blogs, 6)  # 6 blogs per page

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "blogs.html", {
        "page_obj": page_obj
    })
    

def blog_details(request, slug):
    blog = get_object_or_404(Blog, slug=slug)

    return render(request, "blog-details.html", {
        "blog": blog
    })



def gallery(request):
    categories = Category.objects.all()
    images = GalleryImage.objects.select_related("category").order_by("-uploaded_at")
    return render(request, 'gallery.html',{ "categories": categories,"images": images,})

def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your message has been sent successfully!")
            return redirect("contact")
        else:
            messages.error(request, "Please fill all required fields correctly.")
    else:
        form = ContactForm()

    return render(request, "contact.html", {"form": form})

def appointment(request):
    treatments = Treatments.objects.all()
    if request.method == "POST":
        Appointment.objects.create(
            first_name=request.POST.get("first_name"),
            last_name=request.POST.get("last_name"),
            phone=request.POST.get("phone"),
            treatment_id=request.POST.get("treatment"),
            appointment_date=request.POST.get("appointment_date"),
        )
        messages.success(request, "Appointment booked successfully!")
        return redirect("appointment")

    return render(
        request,
        "appointment.html",
        {"treatments": treatments},
    )


    #  404 view\
def page_404(request, exception):
    return render(request, '404.html', status=404)




# --------------Admin----------------



def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not username or not password:
            messages.error(request, "Both fields are required.")
            return render(request, "authenticate/login.html")

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:  # only staff users
            login(request, user)
            messages.success(request, f"Welcome {user.username}!")
            print("login sucesfull")
            return redirect("admin-dashboard")  # change this to your dashboard URL
        else:
            messages.error(request, "Invalid credentials or not an admin.")

    return render(request, "authenticate/login.html")


@login_required(login_url="admin_login")
def admin_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("admin_login")




@login_required(login_url="admin_login")
def admin_dashboard(request):
    stats = {
        'applications_count': Appointment.objects.count(),
        'inquiries_count': ContactMessage.objects.count(),
    }
    
    contacts_count = ContactMessage.objects.count()

    current_year = timezone.now().year

    appt_data = Appointment.objects.filter(
        created_at__year=current_year
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')

    applications_labels = [x['month'].strftime('%b') for x in appt_data]
    applications_counts = [x['count'] for x in appt_data]

    test_data = Testimonial.objects.filter(
        created_at__year=current_year
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')

    testimonials_labels = [x['month'].strftime('%b') for x in test_data]
    testimonials_counts = [x['count'] for x in test_data]


    recent_applications = Appointment.objects.select_related('treatment').order_by('-created_at')[:5]

    recent_inquiries = ContactMessage.objects.order_by('-created_at')[:5]


    context = {
        'stats': stats,
        'contacts_count': contacts_count,
        'recent_applications': recent_applications,
        'recent_inquiries': recent_inquiries,
        
        'applications_labels': json.dumps(applications_labels),
        'applications_counts': json.dumps(applications_counts),
        'testimonials_labels': json.dumps(testimonials_labels),
        'testimonials_counts': json.dumps(testimonials_counts),
    }

    return render(request, "admin_pages/admin-dashboard.html", context)


# --------- Blogs ---------
@login_required(login_url="admin_login")
def blog_list(request):
    blogs_qs = Blog.objects.all().order_by("title")# newest first

    paginator = Paginator(blogs_qs, 6)
    page_number = request.GET.get("page")
    blogs = paginator.get_page(page_number)  # gives a Page object

    return render(request, "admin_pages/blog_list.html", {"blogs": blogs})

@login_required(login_url="admin_login")
def blog_create(request):
    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Blog added successfully!")
            return redirect("blog_list")
    else:
        form = BlogForm()
    return render(request, "admin_pages/create_blog.html", {"form": form})

@login_required(login_url="admin_login")
def blog_update(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            messages.success(request, "Blog updated successfully!")
            return redirect("blog_list")
    else:
        form = BlogForm(instance=blog)
    return render(request, "admin_pages/create_blog.html", {"form": form, "blog": blog})


@login_required(login_url="admin_login")
def blog_delete(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if request.method == "POST":
        blog.delete()
        messages.success(request, "Blog deleted successfully!")
        return redirect("blog_list")
    return render(request, "admin_pages/create_blog.html", {"blog": blog})


# -----------Team Members------------

@login_required(login_url="admin_login")
def list_team(request):
    """Display all team members with pagination"""
    team_members_list = TeamMember.objects.all().order_by(Lower("name"))
    paginator = Paginator(team_members_list, 6)  # Show 10 per page
    page_number = request.GET.get("page")
    team_members = paginator.get_page(
        page_number
    )  # handles invalid pages automatically

    context = {
        "team_members": team_members,
        "title": "Team Members",
    }
    return render(request, "admin_pages/team_list.html", context)


@login_required(login_url="admin_login")
def create_team(request):
    if request.method == "POST":
        form = TeamMemberForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Team member added successfully!")
            return redirect("team_list")
        messages.error(request, "Please correct the errors below.")
    else:
        form = TeamMemberForm()

    return render(request, "admin_pages/add_team.html", {"form": form})


@login_required(login_url="admin_login")
def edit_team_member(request, pk):
    team_member = get_object_or_404(TeamMember, pk=pk)
    if request.method == "POST":
        form = TeamMemberForm(request.POST, request.FILES, instance=team_member)
        if form.is_valid():
            form.save()
            messages.success(request, "Team member updated successfully!")
            return redirect("team_list")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = TeamMemberForm(instance=team_member)

    return render(
        request,
        "admin_pages/team_list.html",
        {"form": form, "team_member": team_member},
    )


@login_required(login_url="admin_login")
def delete_team_member(request, pk):
    team_member = get_object_or_404(TeamMember, pk=pk)
    if request.method == "POST":
        team_member.delete()
        messages.success(request, "Team member deleted successfully!")
        return redirect("team_list")

    return render(request, "admin_pages/team_list.html", {"team_member": team_member})


#---------------Testimonial ------------------

@login_required(login_url="admin_login")
def testimonial_list(request):
    testimonials_list = Testimonial.objects.all().order_by(Lower("name"))
    paginator = Paginator(testimonials_list, 6)
    page_number = request.GET.get("page")
    testimonials = paginator.get_page(page_number)

    return render(
        request, "admin_pages/review_list.html", {"testimonials": testimonials}
    )


@login_required(login_url="admin_login")
def testimonial_create(request):
    if request.method == "POST":
        form = TestimonialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Testimonial added successfully!")
            return redirect("testimonial_list")
    else:
        form = TestimonialForm()
    return render(request, "admin_pages/create_review.html", {"form": form})


@login_required(login_url="admin_login")
def testimonial_update(request, pk):
    testimonial = get_object_or_404(Testimonial, pk=pk)
    if request.method == "POST":
        form = TestimonialForm(request.POST, request.FILES, instance=testimonial)
        if form.is_valid():
            form.save()
            messages.success(request, "Testimonial updated successfully!")
            return redirect("testimonial_list")
    else:
        form = TestimonialForm(instance=testimonial)
    return render(
        request,
        "admin_pages/review_list.html",
        {"form": form, "testimonial": testimonial},
    )


@login_required(login_url="admin_login")
def testimonial_delete(request, pk):
    testimonial = get_object_or_404(Testimonial, pk=pk)
    if request.method == "POST":
        testimonial.delete()
        messages.success(request, "Testimonial deleted successfully!")
        return redirect("testimonial_list")
    return render(request, "admin_pages/review_list.html", {"testimonial": testimonial})


#--------------Galleryyy--------------

@login_required(login_url="admin_login")
def gallery_images(request):
    categories = Category.objects.all().prefetch_related("images")

    category_pages = {}
    for category in categories:
        images_qs = category.images.all().order_by("-uploaded_at")
        paginator = Paginator(images_qs, 8)  # 8 images per page
        page_number = request.GET.get(f"page_{category.id}", 1)

        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        category_pages[category.id] = page_obj

    return render(
        request,
        "admin_pages/image_list.html",
        {
            "categories": categories,
            "category_pages": category_pages,
        },
    )

@login_required(login_url="admin_login")
def add_image(request):
    categories = Category.objects.all()

    if request.method == "POST":
        category_id = request.POST.get("category")
        category = Category.objects.get(id=category_id)
        files = request.FILES.getlist("images")
        print("FILES:", request.FILES)  # Should show uploaded files
        print("FILES count:", len(request.FILES.getlist("images")))

        for file in files:
            GalleryImage.objects.create(
                category=category,
                title=file.name,  # default title = filename
                image=file,
            )
        messages.success(request, "Images uploaded succesfully")
        return redirect("list_image")
    return render(request, "admin_pages/add_image.html", {"categories": categories})

@login_required(login_url="admin_login")
def delete_image(request, image_id):
    image = get_object_or_404(GalleryImage, id=image_id)

    if request.method == "POST":
        image.delete()
        messages.success(request, "Image deleted successfully")
        return redirect("list_image")

    return render(request, "admin_pages/image_list.html", {"image": image})


@login_required(login_url="admin_login")
def category_list(request):
    categories = Category.objects.all().order_by("-created_at")
    paginator = Paginator(categories, 10)
    page_number = request.GET.get("page")
    categories = paginator.get_page(page_number)
    return render(request, "admin_pages/category_list.html", {"categories": categories})


@login_required(login_url="admin_login")
def add_category(request):
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            Category.objects.create(name=name)
            return redirect("category_list")
    return render(request, "admin_pages/add_category.html")


@login_required(login_url="admin_login")
def update_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        category.name = request.POST.get("name")
        category.save()
        return redirect("category_list")
    return redirect("category_list")


@login_required(login_url="admin_login")
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        category.delete()
        return redirect("category_list")
    return redirect("category_list")




# --------- Treatment List ---------
@login_required(login_url="admin_login")
def treatment_list(request):
    treatments_qs = Treatments.objects.all().order_by("created_at")

    paginator = Paginator(treatments_qs, 6)
    page_number = request.GET.get("page")
    treatments = paginator.get_page(page_number)

    return render(
        request,
        "admin_pages/treatment_list.html",
        {"treatments": treatments},
    )


# --------- Treatment Create ---------
@login_required(login_url="admin_login")
def treatment_create(request):
    if request.method == "POST":
        form = TreatmentsForm(request.POST, request.FILES)
        faq_formset = TreatmentFAQFormSet(request.POST)

        if form.is_valid() and faq_formset.is_valid():
            treatment = form.save(commit=False)
            treatment.save()

            faq_formset.instance = treatment
            faq_formset.save()

            messages.success(request, "Treatment and FAQs added successfully!")
            return redirect("treatment_list")
        else:
            print(form.errors)
            print(faq_formset.errors)

    else:
        form = TreatmentsForm()
        faq_formset = TreatmentFAQFormSet()

    return render(
        request,
        "admin_pages/create_treatment.html",
        {
            "form": form,
            "faq_formset": faq_formset,
        },
    )


@login_required(login_url="admin_login")
def treatment_update(request, pk):
    treatment = get_object_or_404(Treatments, pk=pk)

    if request.method == "POST":

        # ------------------------
        # Update Treatment
        # ------------------------
        treatment.title = request.POST.get("title")
        treatment.description = request.POST.get("description")

        if request.FILES.get("image"):
            treatment.image = request.FILES["image"]

        treatment.save()

        # ------------------------
        # Existing FAQs
        # ------------------------
        existing_faq_ids = request.POST.getlist("faq_id[]")

        # Delete removed FAQs
        treatment.faqs.exclude(id__in=existing_faq_ids).delete()

        # Update existing FAQs
        for faq_id in existing_faq_ids:
            question = request.POST.get(f"faq_question_{faq_id}")
            answer = request.POST.get(f"faq_answer_{faq_id}")

            if question and answer:
                faq = TreatmentFAQ.objects.filter(
                    id=faq_id, treatment=treatment
                ).first()

                if faq:
                    faq.question = question
                    faq.answer = answer
                    faq.save()

        # ------------------------
        # New FAQs (added via JS)
        # ------------------------
        for key in request.POST:
            if key.startswith("new_faq_question_"):
                uid = key.replace("new_faq_question_", "")
                question = request.POST.get(key)
                answer = request.POST.get(f"new_faq_answer_{uid}")

                if question and answer:
                    TreatmentFAQ.objects.create(
                        treatment=treatment,
                        question=question,
                        answer=answer
                    )

        messages.success(request, "Treatment updated successfully!")
        return redirect("treatment_list")

    return render(
        request,
        "admin_pages/treatment_list.html",
        {"treatment": treatment},
    )

# --------- Treatment Delete ---------
@login_required(login_url="admin_login")
def treatment_delete(request, pk):
    treatment = get_object_or_404(Treatments, pk=pk)

    if request.method == "POST":
        treatment.delete()
        messages.success(request, "Treatment deleted successfully!")

    return redirect("treatment_list")


# -----------------View Contact--------------
@login_required(login_url="admin_login")
def view_contacts(request):
    inquiries = ContactMessage.objects.all().order_by("created_at")

    # Pagination
    paginator = Paginator(inquiries, 7)  # Show 20 inquiries per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "inquiries": page_obj,
    }
    return render(request, "admin_pages/view_contacts.html", context)

@login_required(login_url="admin_login")
def delete_inquiry(request, pk):
    inquiry = get_object_or_404(ContactMessage, pk=pk)
    if request.method == "POST":
        inquiry.delete()
        return redirect("view_contacts")  # change to your listing view name
    return redirect("view_contacts")


# -----------------View Contact--------------
@login_required(login_url="admin_login")
def view_appointments(request):
    inquiries = Appointment.objects.all().order_by("created_at")

    # Pagination
    paginator = Paginator(inquiries, 7)  # Show 20 inquiries per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "inquiries": page_obj,
    }
    return render(request, "admin_pages/view_appointments.html", context)

@login_required(login_url="admin_login")
def delete_appointment(request, pk):
    inquiry = get_object_or_404(Appointment, pk=pk)
    if request.method == "POST":
        inquiry.delete()
        return redirect("view_appointments")  # change to your listing view name
    return redirect("view_appointments")


