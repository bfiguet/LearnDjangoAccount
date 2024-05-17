from django.db import models
from django .contrib.auth.models import AbstractBaseUser, BaseUserManager

class MyAccountManager(BaseUserManager):
	def create_user(self, email, username, password=None):
		if not email:
			raise ValueError("Users must have an email address")
		if not username:
			raise ValueError("Users must have a username")
		user = self.model(
			email=self.normalize_email(email),
			username=username,
		)
		user.set_password(password)
		user.save(using=self._db)
		return user
	
	def create_superuser(self, email, username, password):
		user = self.create_user(
			email=self.normalize_email(email),
			username=username,
			password=password,
		)
		user.is_admin = True
		user.is_staff = True
		user.is_superuser = True
		user.save(using=self._db)
		return user
	
def get_profile_image_filepath(self):
	return 'profile_images/' + str(self.username) + '.jpeg'

def get_default_profile_image():
	return "profile_images/profile.jpeg"

class Account(AbstractBaseUser):
	email = models.EmailField(verbose_name="email", max_length=60, unique=True)
	username = models.CharField(max_length=30, unique=True)
	profile_image = models.ImageField(max_length=255, upload_to=get_profile_image_filepath, null=True, blank=True, default=get_default_profile_image)
	is_admin = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)
	is_staff = models.BooleanField(default=False)
	is_superuser = models.BooleanField(default=False)
	
	USERNAME_FIELD = 'username'
	REQUIRED_FIELDS = ['email']
	
	objects = MyAccountManager()

	def __str__(self):
		return self.username
	
	#def get_profile_image_filename(self):
	#	return str(self.profile_image)[str(self.profile_image).index('profile_image/' + str):]

	def get_profile_image_filename(instance, filename):
		return '/'.join(['profile_images', instance.user.username, filename])

	def has_perm(self, perm, obj=None):
		return self.is_admin
	
	def has_module_perms(self, app_label):
		return True
	
