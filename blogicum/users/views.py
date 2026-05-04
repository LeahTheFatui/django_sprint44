from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView
from django.shortcuts import get_object_or_404
from blog.models import Post
from blog.utils import paginate_queryset
from django.db.models import Count


class RegistrationView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('login')


class ProfileView(DetailView):
    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_user = self.get_object()

        if self.request.user == profile_user:
            posts = Post.objects.filter(author=profile_user)
        else:
            posts = Post.objects.filter(
                author=profile_user,
                is_published=True,
                category__is_published=True
            )

        posts = posts.annotate(comment_count=Count('comments')).order_by('-pub_date')

        context['page_obj'] = paginate_queryset(self.request, posts)
        return context
