from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from userprofile.forms import UserForm, UserProfileForm


# registration view
def register(request):

    # create flag for successful registration
    registered = False

    # if submitted, process form
    if request.method == 'POST':

        # grab information from forms
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # if those are valid, continue
        if user_form.is_valid() and profile_form.is_valid():

            # save user form to database
            user = user_form.save()

            # hash password and send to user object
            user.set_password(user.password)

            # Add user to user group
            user.groups.add(Group.objects.get(name='customer'))

            # save user
            user.save()

            # prepare userprofile form
            profile = profile_form.save(commit=False)

            # connect userprofile with user
            profile.user = user

            # if profile picture provided, save it
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture'] 

            # save userprofile
            profile.save()

            # flag successful registration
            registered = True

        # else forms invalid, print errors
        else:
            print(user_form.errors, profile_form.errors)

    # else show the registration form
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render the template depending on the context.
    return render(request, 'userprofile/register.html',
                      {'user_form': user_form,
                       'profile_form': profile_form,
                       'registered': registered})


# login view
def user_login(request):

    # if submitted, process form
    if request.method == 'POST':

        # get username and password
        username = request.POST.get('username')
        password = request.POST.get('password')

        # authenticate: if successful, user object returned
        user = authenticate(username=username,password=password)

        # if successful authentication
        if user:

            # check if active
            if user.is_active:

                # login and return to homepage
                login(request, user)
                return HttpResponseRedirect(reverse('index'))

            # else return error page
            else:
                return HttpResponse("Your account is disabled. Please contact the system administrator.")

        # else bad login details, return error page
        else:
            print("Invalid authentication details.")
            return HttpResponse("Invalid authentication details")

    # else render login form
    else:
        return render(request, 'userprofile/login.html', {})

# logout view
@login_required
def user_logout(request):

    # logout user
    logout(request)

    # Take the user back to the hompage
    return render(request, 'userprofile/logout.html')


# view profile view
@login_required
def view_current_profile(request):
    return render(request, 'userprofile/viewprofile.html')