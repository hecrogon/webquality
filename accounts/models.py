from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _ 
from userena.models import UserenaBaseProfile

class Base(models.Model):
	creation_date = models.DateTimeField('creation date', auto_now_add = True)
	modification_date = models.DateTimeField('modification date', auto_now = True)

	class Meta:
		abstract = True

class UserProfile(UserenaBaseProfile, Base):
	user = models.OneToOneField(User, unique=True, verbose_name=_('user'), related_name='userprofile')

	def __unicode__(self):
		return self.user.username

def content_file_name(instance, filename):
	instance.filename = filename
	return '/'.join(['static/images/pictures', datetime.datetime.now().strftime("%Y%m%d%H%M%S") + filename])

class UserProfilePicture(Base):
	userprofile = models.ForeignKey(UserProfile, verbose_name=_("User Profile"), related_name="pictures")
	picture = models.ImageField(upload_to=content_file_name, blank = True, verbose_name=_('Picture'), help_text=_("Select a picture to upload"))
	filename = models.CharField(max_length=200, verbose_name=_("File Name"), blank=True)
	text = models.CharField(max_length=200, verbose_name=_("Description"), blank=True)
	is_main = models.BooleanField(verbose_name=_("Main picture"))

	def __unicode__(self):
		return "(%s)-%s"%(self.userprofile.name, self.filename)

