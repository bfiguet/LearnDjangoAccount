from django.db import models
from django.conf import settings
from django.utils import timezone

class FriendList(models.Model):

	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user")
	friends = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="friends")

	def __str__(self):
		return self.user.username
	
	def add_friend(self, account):
		if not account in self.friends.all():
			self.friends.add(account)
			#self.save()

	def remove_friend(self, account):
		if account in self.friends.all():
			self.friends.remove(account)

	def unfriend(self, removee):
		#initiate the action of unfriending someone
		#remover_friend_list = self # personn terminating the friendship

		# Remove friend from removee friend list
		removee_friend_list = FriendList.objects.get(user=removee)
		removee_friend_list.remove_friend(self.user)

		# Remove friend from current user friend list
		self.remove_friend(removee)

	def is_mutual_friend(self, friend):
		#is this a friend?
		if friend in self.friends.all():
			return True
		return False
	

class FriendRequest(models.Model):
 #A friends request consists of two main parts:
	# 1. SENDER:
		#- The person sending/initiating the friend request
	# 2. RECEIVER:
		#- The person receiving the friend request
	
	sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sender")
	receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="receiver")

	is_active = models.BooleanField(blank=True, null=False, default=True)
	timestamp = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.sender.username
	
	def accept(self):
		#Accept a friend request
		#Update both SENDER and RECEIVER friend list
		receiver_friend_list = FriendList.objects.get(user=self.receiver)
		if receiver_friend_list:
			receiver_friend_list.add_friend(self.sender)
			sender_friend_list = FriendList.objects.get(user=self.sender)
			if sender_friend_list:
				sender_friend_list.add_friend(self.receiver)
				self.is_active = False
				self.save()

	
	def decline(self):
		#Decline a friend request
		#It is "declined" by setting the "is_active" field to False
		self.is_active = False
		self.save()

	def cancel(self):
		#Cancel a friend request
		#It is "canceled" by setting the "is_active" field to False
		#this is different with respect to "declining" through the notification that is generated
		self.is_active = False
		self.save()