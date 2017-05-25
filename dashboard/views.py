from django.shortcuts import render, reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from utils.mailer import EmailHelper
from dspconnector.connector import DSPConnector, DSPConnectorException
from .models import Profile, Invitation
from .exceptions import EmailAlreadyUsed, UserAlreadyInvited
from django.http import HttpResponseRedirect


@login_required()
def dashboard(request):
    try:
        context = {'themes': DSPConnector.get_themes()}
    except DSPConnectorException as e:
        context = {'themes': []}
        messages.error(request, e.message)
    return render(request, 'dashboard/dashboard.html', context)


@login_required()
def theme(request, theme_name):
    try:
        # feeds = DSPConnector.get_feeds(theme_name)
        feeds = {}
        influencers = DSPConnector.get_influencers(theme_name)
        themes = DSPConnector.get_themes()
        themes_list = [t.get('name', '') for t in themes.get('themes', []) if t.get('name', '') != theme_name]
    except DSPConnectorException as e:
        messages.error(request, e.message)
        feeds = []
        influencers = []
        themes_list = []

    context = {'theme_name': theme_name,
               'feeds': feeds.get('feeds', []),
               'themes': themes_list,
               'influencers': influencers.get('influencers', [])}
    return render(request, 'dashboard/theme.html', context)


@login_required()
def profile(request, profile_id=None):
    try:
        if profile_id:
            user_profile = Profile.get_by_id(profile_id)
        else:
            user_profile = Profile.get_by_email(request.user.email)
    except Profile.DoesNotExist:
        return HttpResponseRedirect(reverse('dashboard:dashboard'))
    context = {'profile': user_profile}
    return render(request, 'dashboard/profile.html', context)


@login_required()
def search_members(request):
    return render(request, 'dashboard/search_members.html', {})


def privacy(request):
    return render(request, 'dashboard/privacy.html', {})


@login_required()
def invite(request):
    if request.method == 'POST':
        try:
            address = request.POST['email']
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
        except KeyError:
            messages.error(request, 'Please all the fields are required!')
            return HttpResponseRedirect(reverse('dashboard:invite'))

        # email not present, filling invitation model
        try:
            invitation = Invitation.create(user=request.user, email=address, first_name=first_name, last_name=last_name)
            subject = 'INVITATION To OpenMake Digital Social Platform'
            content = '''
Hello {}!
Our member {} invited you to the DSP bla bla bla..
'''.format(invitation.first_name, invitation.profile.user.get_full_name())
            EmailHelper.send_email(
                message=content,
                subject=subject,
                receiver_email=address,
                receiver_name=''
            )
            messages.success(request, 'Invitation sent!')
        except EmailAlreadyUsed:
            messages.error(request, 'User is already a member!')
        except UserAlreadyInvited:
            messages.error(request, 'User has already received an invitation!')
        except Exception:
            messages.error(request, 'Please try again!')

    return render(request, 'dashboard/invite.html', {})


def support(request):
    return render(request, 'dashboard/support.html', {})


def terms_conditions(request):
    return render(request, 'dashboard/terms_conditions.html', {})
