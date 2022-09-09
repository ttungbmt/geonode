import json

from django.utils import timezone
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from geonode.geoserver.createlayer.forms import NewLayerForm
from django.template.defaultfilters import slugify
from geonode.geoserver.createlayer.utils import create_layer
from django.shortcuts import redirect

from guardian.models import Group

from oauth2_provider.models import AccessToken
from oauth2_provider.exceptions import OAuthToolkitError, FatalClientError
from allauth.account.utils import user_field, user_email, user_username

from ..utils import json_response
from ..decorators import superuser_or_apiauth
from ..base.auth import (
    get_token_object_from_session,
    extract_headers,
    get_auth_token)

def verify_access_token(request, key):
    try:
        token = None
        if request:
            token = get_token_object_from_session(request.session)
        if not token or token.key != key:
            token = AccessToken.objects.get(token=key)
        if not token.is_valid():
            raise OAuthToolkitError('AccessToken is not valid.')
        if token.is_expired():
            raise OAuthToolkitError('AccessToken has expired.')
    except AccessToken.DoesNotExist:
        raise FatalClientError("AccessToken not found at all.")
    except Exception:
        return None
    return token

@csrf_exempt
def createlayer(request):

    if (request.POST and 'token' in request.POST):
        token = None
        try:
            access_token = request.POST.get('token')
            token = verify_access_token(request, access_token)
        except Exception as e:
            return HttpResponse(
                json.dumps({
                    'error': str(e)
                }),
                status=403,
                content_type="application/json"
            )

        if token:
            form = NewLayerForm(request.POST)
            if form.is_valid():
                try:
                    ## Create layer
                    name = form.cleaned_data['name']
                    name = slugify(name.replace(".", "_"))
                    title = form.cleaned_data['title']
                    geometry_type = form.cleaned_data['geometry_type']
                    attributes = form.cleaned_data['attributes']
                    permissions = form.cleaned_data["permissions"]
                    layer = create_layer(name, title, token.user.username, geometry_type, attributes)
                    layer.set_permissions(json.loads(permissions))
                    # Return success message
                    data = json.dumps({
                        'msg': 'Create Layer Success',
                        'success': True,
                        'layer': {
                            'name': layer.name,
                            'title': layer.title,
                            'alternate': layer.alternate,
                            'uuid': layer.uuid,
                            'pk': layer.pk
                        }
                    })

                    response = HttpResponse(
                        data,
                        content_type="application/json"
                    )
                    response["Authorization"] = f"Bearer {access_token}"
                    return response
                
                except Exception as e:
                    error = f'{e} ({type(e)})'
                    print(error)
        else:
            return HttpResponse(
                json.dumps({
                    'error': 'No access_token from server.'
                }),
                status=403,
                content_type="application/json"
            )

    return HttpResponse(
        json.dumps({
            'error': 'invalid_request'
        }),
        status=403,
        content_type="application/json"
    )