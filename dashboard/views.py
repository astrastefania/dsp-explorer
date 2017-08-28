import pytz
from django.contrib.auth.models import User
from datetime import datetime
from django.shortcuts import render, reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site

from crmconnector import capsule
from utils.mailer import EmailHelper
from utils.hasher import HashHelper
from dspconnector.connector import DSPConnector, DSPConnectorException
from .models import Profile, Invitation, Feedback, Tag
from .exceptions import EmailAlreadyUsed, UserAlreadyInvited
from django.http import HttpResponseRedirect
from form import FeedbackForm
from utils.emailtemplate import invitation_base_template_header, invitation_base_template_footer, invitation_email_receiver
import datetime as dt
import json
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import logging


@login_required()
def dashboard(request):
    try:
        import random
        themes = DSPConnector.get_themes()['themes']
        random_theme = themes[random.randint(0, len(themes) - 1)]
        random_theme_name = random_theme['name']
        random_feeds = DSPConnector.get_feeds(random_theme_name)['feeds'][:4]
        top_influencers = DSPConnector.get_influencers(random_theme_name)['influencers'][:4]
        other_themes = [t.get('name', '') for t in themes if t.get('name', '') != random_theme_name]
    except DSPConnectorException:
        random_theme_name = 'Not Provided'
        random_feeds = []
        top_influencers = []
        messages.error(request, 'Some error occures, please try again')
        other_themes = []
        
    hot_tags = [t[0] for t in Profile.get_hot_tags(6)]
    last_members = Profile.get_last_n_members(3)
    context = {'themes': other_themes,
               'last_members': last_members,
               'hot_tags': hot_tags,
               'random_theme_name': random_theme_name,
               'random_feeds': random_feeds,
               'top_influencers': top_influencers}
    return render(request, 'dashboard/dashboard.html', context)

@login_required()
def theme(request, theme_name):
    try:
        themes = DSPConnector.get_themes()
        themes_list = [t.get('name', '') for t in themes.get('themes', []) if t.get('name', '') != theme_name]
    except DSPConnectorException as e:
        messages.error(request, e.message)
        themes_list = {}
    
    context = {'theme_name': theme_name,
               'themes': themes_list}
    return render(request, 'dashboard/theme.html', context)


@login_required()
def profile(request, profile_id=None, action=None):
    try:
        if profile_id:
            user_profile = Profile.get_by_id(profile_id)
        else:
            user_profile = Profile.get_by_email(request.user.email)
    except Profile.DoesNotExist:
        return HttpResponseRedirect(reverse('dashboard:dashboard'))

    if request.method == 'POST':
        new_profile = {}
        new_user = {}
        try:
            new_user['first_name'] = request.POST['first_name'].title()
            new_user['last_name'] = request.POST['last_name'].title()
            new_profile['gender'] = request.POST['gender']
            new_profile['birthdate'] = datetime.strptime(request.POST['birthdate'], '%Y/%m/%d')
            new_profile['birthdate'] = pytz.utc.localize(new_profile['birthdate'])
            new_profile['city'] = request.POST['city']
            new_profile['occupation'] = request.POST['occupation']
            new_profile['twitter_username'] = request.POST.get('twitter', '')
            tags = request.POST['tags']
        except ValueError:
            messages.error(request, 'Incorrect birthdate format: it must be YYYY/MM/DD')
            return HttpResponseRedirect(reverse('dashboard:profile',  kwargs={'profile_id': user_profile.id, 'action':action}))
        except KeyError:
            print(KeyError)
            messages.error(request, 'Please fill the required fields!')
            return HttpResponseRedirect(reverse('dashboard:profile',  kwargs={'profile_id': user_profile.id, 'action':action}))

        # check birthdate
        if new_profile['birthdate'] > pytz.utc.localize(datetime(dt.datetime.now().year - 13, *new_profile['birthdate'].timetuple()[1:-2])):
            messages.error(request, 'You must be older than thirteen')
            return HttpResponseRedirect(reverse('dashboard:profile',  kwargs={'profile_id': user_profile.id, 'action':action}))

        # Update image
        try:
            imagefile = request.FILES['profile_img']
            filename, file_extension = os.path.splitext(imagefile.name)

            allowed_extensions = ['.jpg', '.jpeg', '.png']
            if not (file_extension in allowed_extensions):
                raise ValueError

            imagefile.name = str(datetime.now().microsecond) + '_' + str(imagefile._size) + file_extension

        except ValueError as exc:
            messages.error(request, 'Profile Image is not an image file')
            return HttpResponseRedirect(reverse('dashboard:onboarding'))
        except KeyError as exc:
            imagefile = request.user.profile.picture
        except Exception as exc:
            messages.error(request, 'Error during image upload, please try again')
            logging.error('[VALIDATION_ERROR] Error during image upload: {USER} , EXCEPTION {EXC}'.format(
                USER=request.user.email, EXC=exc
            ))
            return HttpResponseRedirect(reverse('dashboard:onboarding'))
        new_profile['picture'] = imagefile

        user = User.objects.filter(email=request.user.email).first()

        # Update user fields
        user.__dict__.update(new_user)
        user.save()
        # Update profile fields
        user.profile.__dict__.update(new_profile)
        user.profile.save()

        user.profile.tags.through.objects.all().delete()

        # Update tags
        for tagName in map(lambda x: x.lower().capitalize(), tags.split(",")):
            user.profile.tags.add(Tag.create(name=tagName))

        # Check for user on Capsule CRM
        crmUser = capsule.CRMConnector.search_party_by_email(user.email)
        if crmUser:
            try:
                capsule.CRMConnector.update_party(crmUser['id'], {'party': {
                    'emailAddresses': [{'id': crmUser['emailAddresses'][0]['id'], 'address': user.email}],
                    'type': 'person',
                    'firstName': user.first_name,
                    'lastName': user.last_name,
                    'jobTitle': user.profile.occupation,
                    'pictureURL': user.profile.picture.url
                }
                })
            except:
                messages.error(request, 'Some error occures, please try again!')
                logging.error('[VALIDATION_ERROR] Error during CRM Creation for user: %s' % crmUser.id)
                # TODO SEND ERROR EMAIL TO ADMIN
                return HttpResponseRedirect(reverse('dashboard:dashboard'))
        else:
            print('[ ERROR ] : user not found on CRM during update ! for user : %s' % crmUser.id)
            logging.error('[ ERROR ] : user not found on CRM during update ! for user : %s' % crmUser.id)

        messages.success(request, 'Profile updated!')
        return HttpResponseRedirect(reverse('dashboard:profile'))

    user_profile.jsonTags = json.dumps(map(lambda x: x.name, user_profile.tags.all()))

    context = {
        'profile': user_profile,
        'profile_action': action,
        'is_my_profile': request.user.profile.id == user_profile.id,
        'tags': json.dumps(map(lambda x: x.name, Tag.objects.all()))
    }

    return render(request, 'dashboard/profile.html', context)


@login_required()
def search_members(request, search_string=0):
    return render(request, 'dashboard/search_members.html', {'search_string': search_string})


@login_required()
def invite(request):
    if request.method == 'POST':
        try:
            address = request.POST['email'].lower()
            first_name = request.POST['first_name'].title()
            last_name = request.POST['last_name'].title()
        except KeyError:
            messages.error(request, 'Please all the fields are required!')
            return HttpResponseRedirect(reverse('dashboard:invite'))
        
        try:
            User.objects.get(email=address)
            messages.error(request, 'User is already a DSP member!')
            return HttpResponseRedirect(reverse('dashboard:invite'))
        except User.DoesNotExist:
            pass
        
        try:
            Invitation.objects.get(receiver_email=HashHelper.md5_hash(address))
            messages.error(request, 'User is been already invited!')
            return HttpResponseRedirect(reverse('dashboard:invite'))
        except Invitation.DoesNotExist:
            pass
        
        # email not present, filling invitation model
        try:
    
            Invitation.create(user=request.user,
                              sender_email=request.user.email,
                              sender_first_name=request.user.first_name,
                              sender_last_name=request.user.last_name,
                              receiver_first_name=first_name,
                              receiver_last_name=last_name,
                              receiver_email=address,
                              )

            subject = 'You are invited to join the OpenMaker community!'
            content = "{}{}{}".format(invitation_base_template_header,
                                      invitation_email_receiver.format(RECEIVER_FIRST_NAME=first_name,
                                                                       RECEIVER_LAST_NAME=last_name,
                                                                       SENDER_FIRST_NAME=request.user.first_name,
                                                                       SENDER_LAST_NAME=request.user.last_name,
                                                                       ONBOARDING_LINK=request.build_absolute_uri('/onboarding/')),
                                      invitation_base_template_footer)

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
        except Exception as e:
            print e.message
            messages.error(request, 'Please try again!')
    
    return render(request, 'dashboard/invite.html', {})


@login_required()
def feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            try:
                Feedback(user=request.user, title=request.POST['title'],
                         message_text=request.POST['message_text']).save()
                messages.success(request, 'Thanks for your feedback!')
            except KeyError:
                messages.warning(request, 'Error, please try again.')
        else:
            messages.error(request, 'Please all the fields are required!')
    return HttpResponseRedirect(reverse('dashboard:dashboard'))
