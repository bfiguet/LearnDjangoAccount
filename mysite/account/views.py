from django.shortcuts import render, redirect
from .models import Account
from django.http import HttpResponse
from django.conf import settings
from .forms import AccountUpdateForm, RegistrationForm, AccountAuthenticationForm
from django.contrib.auth import authenticate, login, logout

def register_view(request, *args, **kwargs):
	user = request.user
	if user.is_authenticated:
		return HttpResponse("You are already authenticated as " + str(user.username))
	context = {}
	if request.POST:
		form = RegistrationForm(request.POST)
		if form.is_valid():
			form.save()
			email = form.cleaned_data.get('email').lower()
			raw_password = form.cleaned_data.get('password1')
			account = authenticate(email=email, password=raw_password)
			login(request, account)
			#destination = kwargs.get("next")
			destination = get_redirect_if_exists(request)
			if destination: #if destination != None
				return redirect(destination)
			return redirect("home")
		else:
			context['registration_form'] = form
	else:
		form = RegistrationForm()
		context['registration_form'] = form
	return render(request, 'account/register.html', context)

def account_view(request, *args, **kwargs):
	context = {}
	user_id = kwargs.get("user_id")
	try:
		account = Account.objects.get(pk=user_id)
	except Account.DoesNotExist:
		return HttpResponse("That user does not exist.")
	if account:
		context['id'] = account.id
		context['username'] = account.username
		context['email'] = account.email
		context['profile_image'] = account.profile_image
		context['hide_email'] = account.hide_email
		
		# Define state template variables

		is_self = True
		is_friend = False
		user = request.user
		if user.is_authenticated and user != account:
			is_self = False
			if user.friends_list.is_mutual_friend(account):
				is_friend = True
		elif not user.is_authenticated:
			is_self = False

		context['is_self'] = is_self
		context['is_friend'] = is_friend
		context['BASE_URL'] = settings.BASE_URL

	return render(request, 'account/account.html', context)

def edit_account_view(request, *args, **kwargs):
	if not request.user.is_authenticated:
		return redirect("login")
	user_id = kwargs.get("user_id")
	try:
		account = Account.objects.get(pk=user_id)
	except Account.DoesNotExist:
		return HttpResponse("That user does not exist.")
	if account.pk != request.user.pk:
		return HttpResponse("You cannot edit someone else's profile.")
	context = {}
	if request.POST:
		form = AccountUpdateForm(request.POST, request.FILES, instance=request.user)
		if form.is_valid():
			#delete old profile image so the name is preserved
			account.profile_image.delete()
			form.save()
			return redirect("account:view", user_id=account.pk)
		else:
			form = AccountUpdateForm(request.POST, instance=request.user, 
				initial={
					"id": account.pk,
					"email": account.email,
					"username": account.username,
					"profile_image": account.profile_image,
					"hide_email": account.hide_email,
				}
			)
			context['form'] = form
	else:
		form = AccountUpdateForm(
			initial={
				"id": account.pk,
				"email": account.email,
				"username": account.username,
				"profile_image": account.profile_image,
				"hide_email": account.hide_email,
			}
		)
		context['form'] = form
	context['DATA_UPLOAD_MAX_MEMORY_SIZE'] = settings.DATA_UPLOAD_MAX_MEMORY_SIZE
	return render(request, 'account/edit_account.html', context)

def logout_view(request):
	logout(request)
	return redirect("home")

def login_view(request, *args, **kwargs):
	context = {}
	user = request.user
	if user.is_authenticated:
		return redirect("home")
	
	if request.POST:
		form = AccountAuthenticationForm(request.POST)
		if form.is_valid():
			#form.save()
			username = request.POST['username']
			password = request.POST['password']
			user = authenticate(username=username, password=password)
			if user:
				login(request, user)
				destination = get_redirect_if_exists(request)
				if destination:
					return redirect(destination)
				return redirect("home")
	else:
		form = AccountAuthenticationForm()
	context['login_form'] = form
	return render(request, "account/login.html", context)

def get_redirect_if_exists(request):
	redirect = None
	if request.GET:
		if request.GET.get("next"):
			redirect = str(request.GET.get("next"))
	return redirect