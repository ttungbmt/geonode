from django.conf.urls import url
from . import views


urlpatterns = [
    url(
        r'^createlayer/$',
        views.createlayer,
        name='becagis_createlayer'
    ),
]
