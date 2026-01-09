from django.urls import path,include
from .import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

    path('', views.index, name= 'index'),
    path('about/', views.about, name= 'about'),
    path('our-doctors/', views.our_doctors, name= 'our_doctors'),
    path("treatments/", views.treatments, name="treatments"),
    

    path("blogs/", views.blogs, name="blogs"),
    path("blogs/<slug:slug>/", views.blog_details, name="blog_details"),

    path('gallery/', views.gallery, name= 'gallery'),
    path('contact/', views.contact, name= 'contact'),
    path('appointment/', views.appointment, name= 'appointment'),

    
   



    # -------------Admin--------------

    path("login/", views.admin_login, name="admin_login"),
    path("admin-logout/", views.admin_logout, name="admin_logout"),
    path("admin-dashboard/", views.admin_dashboard, name="admin-dashboard"),

     # Blogs
    path("view-blogs/", views.blog_list, name="blog_list"),
    path("add-blogs/", views.blog_create, name="blog_create"),
    path("view-blogs/<int:pk>/edit/", views.blog_update, name="blog_update"),
    path("view-blogs/<int:pk>/delete/", views.blog_delete, name="blog_delete"),
    # Team
    path("add-team/", views.create_team, name="team_add"),
    path("view-team/", views.list_team, name="team_list"),
    path("team/<int:pk>/edit/", views.edit_team_member, name="edit_team_member"),
    path("team/<int:pk>/delete/", views.delete_team_member, name="delete_team_member"),
    # Testimonial
    path("view-testimonials/", views.testimonial_list, name="testimonial_list"),
    path("add-review", views.testimonial_create, name="testimonial_create"),
    path("testimonials/<int:pk>/edit/",views.testimonial_update,name="testimonial_update"),
    path("testimonials/<int:pk>/delete/",views.testimonial_delete,name="testimonial_delete"),
    # Galllerry
    path("list-images/", views.gallery_images, name="list_image"),
    path("add_image/", views.add_image, name="add_image"),
    path("delete-image/<int:image_id>/", views.delete_image, name="delete_image"),

    path("categories/", views.category_list, name="category_list"),
    path("categories/add/", views.add_category, name="add_category"),
    path("categories/update/<int:pk>/", views.update_category, name="update_category"),
    path("categories/delete/<int:pk>/", views.delete_category, name="delete_category"),

    # Treatment
    path("view-treatments/", views.treatment_list, name="treatment_list"),
    path("treatments/create/", views.treatment_create, name="treatment_create"),
    path("treatment/update/<int:pk>/", views.treatment_update, name="treatment_update"),
    path("treatments/delete/<int:pk>/", views.treatment_delete, name="treatment_delete"),

    path("treatments/<slug:slug>/", views.treatment_details, name="treatment_details"),

    # View Contacts
    path("view-contacts/", views.view_contacts, name="view_contacts"),
    path("delete/<int:pk>/", views.delete_inquiry, name="delete_inquiry"),

    # View Appointments
    path("view-appointments/", views.view_appointments, name="view_appointments"),
    path("delete/<int:pk>/", views.delete_appointment, name="delete_appointment"),
     




    ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
handler404 = 'dream_casa_app.views.page_404'