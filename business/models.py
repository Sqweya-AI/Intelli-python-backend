from django.db import models


# owner is the User that create the organization/Business, 
# add the user object from the users or accounts app when ready 

class Business(models.Model):
    name       = models.CharField(max_length=300)
    slug       = models.SlugField(max_length=300)
    owner      = models.EmailField()
    org_id     = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self) -> str:
        return self.name + ' ' + self.org_id