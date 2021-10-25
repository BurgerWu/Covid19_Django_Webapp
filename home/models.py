#import libraries
from django.db import models
from django.db.models.fields import AutoField


class FeedBack(models.Model):
    """Create feedback model so that users can submit their feedback"""
    
    #Define each field of the model and characterize them
    id = AutoField(primary_key=True)
    Date = models.DateTimeField(blank = False, null = False)
    Name = models.CharField(max_length = 20, blank = True, null = True)
    Email = models.CharField(max_length = 50, blank = True, null = True)
    FeedBack = models.TextField(blank = False, null = False)

    def __str__(self):
        """String for representing the Model object"""
        return str(self.Date) + '-' + self.Name

