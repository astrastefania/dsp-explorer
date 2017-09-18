from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import *
from django.contrib import messages
from django.urls import reverse
from .models import Application
from dashboard.models import Profile
from django.contrib.admin.views.decorators import staff_member_required
import logging, os
from django.views.static import serve

@login_required
def application(request):
    if request.method == 'POST':
        allowed_extensions = ['.pdf']
        try:
            project_name = request.POST['project_name'].strip().title()
            les_choice = int(request.POST.getlist('les_choice')[0])

            # check zipfile --> now is a pdf
            zip_location = request.FILES['zip_location']
            filename, file_extension = os.path.splitext(zip_location.name)
            if not (file_extension in allowed_extensions):
                raise ValueError('notvalid')

            if not project_name or not zip_location:
                raise KeyError

            # limit to 1MB
            if zip_location.size > 10485760:
                raise ValueError('sizelimit')

        except ValueError as exc:
            if str(exc) == 'sizelimit':
                logging.info('ERROR - File size uploaded is larger than 10Mb')
                messages.error(request, 'File size uploaded must be smaller than 10Mb')
            elif str(exc) == 'notvalid':
                logging.info('ERROR - File uploaded extension is not valid')
                messages.error(
                    request,
                    'File uploaded extension is not valid, ( must be : %s )' % ', '.join(allowed_extensions)
                )
            else:
                logging.info('ERROR - Please fill all the fields')
                messages.error(request, 'Please fill all the fields')
            return HttpResponseRedirect(reverse('pss:application'))

        except (KeyError, IndexError):
            logging.info('ERROR - Please fill all the fields')
            messages.error(request, 'Please fill all the fields')
            return HttpResponseRedirect(reverse('pss:application'))
        app = Application(project_name=project_name,
                          les=les_choice,
                          zip_location=zip_location,
                          profile=Profile.objects.get(user=request.user))
        app.save()
        messages.success(request, 'Thanks for your submission!')
        app.send_email()
    return render(request, 'pss/application.html', {'les_choices': Application.les_choices})


@staff_member_required(login_url='dashboard:login')
def application_result(request):
    context = {'applications': Application.objects.all()}
    return render(request, 'pss/application_result.html', context)


@staff_member_required(login_url='dashboard:login')
def application_pdf(request, application_id):

    if not application_id:
        return HttpResponse(open('pss/application/PSS_application_form.pdf', 'r').read(), content_type='application/pdf')

    application = Application.objects.get(pk=application_id)

    if request.user.is_superuser == 1 or Application.get(application_id)['profile_id'] == request.user.profile.id:
        return HttpResponse(open('pss/%s' % application.zip_location, 'r').read(), content_type='application/pdf')




