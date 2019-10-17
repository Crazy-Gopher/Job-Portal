import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView

from jobsapp.decorators import user_is_employer
from jobsapp.forms import CreateJobForm
from jobsapp.models import Job, Applicant
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from jobsapp.serializers import JobSerializer

class DashboardView(ListView):
    model = Job
    template_name = 'jobs/employer/dashboard.html'
    context_object_name = 'jobs'

    @method_decorator(login_required(login_url=reverse_lazy('accounts:login')))
    @method_decorator(user_is_employer)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(self.request, *args, **kwargs)

    def get_queryset(self):
        return self.model.objects.filter(user_id=self.request.user.id)


class ApplicantPerJobView(ListView):
    model = Applicant
    template_name = 'jobs/employer/applicants.html'
    context_object_name = 'applicants'
    paginate_by = 1

    @method_decorator(login_required(login_url=reverse_lazy('accounts:login')))
    @method_decorator(user_is_employer)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(self.request, *args, **kwargs)

    def get_queryset(self):
        return Applicant.objects.filter(job_id=self.kwargs['job_id']).order_by('id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['job'] = Job.objects.get(id=self.kwargs['job_id'])
        return context



def JobCreateView(request):
    if not request.user.is_authenticated:
        return reverse_lazy('accounts:login')
    if request.user.is_authenticated and request.user.role != 'employer':
        return reverse_lazy('accounts:login')

    if request.method == "POST":
        form = CreateJobForm(request.POST)
        form.instance.user = request.user
        if form.is_valid():
            post = form.save()
            #return redirect('jobs-detail', pk=post.pk)
            return redirect('jobs:employer-dashboard')
        return render(request, 'jobs/create.html', {'form' : form})
    else:
        form = CreateJobForm()
    return render(request, 'jobs/create.html', {'form' : form})


class ApplicantsListView(ListView):
    model = Applicant
    template_name = 'jobs/employer/all-applicants.html'
    context_object_name = 'applicants'

    def get_queryset(self):
        # jobs = Job.objects.filter(user_id=self.request.user.id)
        return self.model.objects.filter(job__user_id=self.request.user.id)


@login_required(login_url=reverse_lazy('accounts:login'))
def filled(request, job_id=None):
    job = Job.objects.get(user_id=request.user.id, id=job_id)
    job.filled = True
    job.save()
    return HttpResponseRedirect(reverse_lazy('jobs:employer-dashboard'))

@login_required(login_url=reverse_lazy('accounts:login'))
def delete_job(request, job_id=None):
    job = Job.objects.get(user_id=request.user.id, id=job_id)
    job.delete()
    return HttpResponseRedirect(reverse_lazy('jobs:employer-dashboard'))


@login_required(login_url=reverse_lazy('accounts:login'))
def edit_job(request, job_id=None): 
    instance = get_object_or_404(Job, id=job_id)
    
    if request.method == 'POST':
        form = CreateJobForm(request.POST or None, instance=instance)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect(reverse_lazy('jobs:employer-dashboard'))
    else:
        serializer = JobSerializer(instance)
        form = CreateJobForm(request.POST or None, instance=instance)
    return render(request, 'jobs/update.html', {'form' : form, 'data': serializer.data})
