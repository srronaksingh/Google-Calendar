from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from google.auth.transport import requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from rest_framework.decorators import api_view

@csrf_exempt
@api_view(['GET'])
def GoogleCalendarInitView(request):
    flow = Flow.from_client_secrets_file(
        'path/to/client_secrets.json',
        scopes=['https://www.googleapis.com/auth/calendar.readonly'],
        redirect_uri='http://localhost:8000/rest/v1/calendar/redirect/'
    )

    authorization_url, state = flow.authorization_url(prompt='consent')
    request.session['state'] = state

    return HttpResponse(authorization_url)

@csrf_exempt
@api_view(['GET'])
def GoogleCalendarRedirectView(request):
    code = request.GET.get('code')
    state = request.GET.get('state')
    
    if state != request.session['state']:
        return HttpResponse('Invalid state parameter')

    flow = Flow.from_client_secrets_file(
        'path/to/client_secrets.json',
        scopes=['https://www.googleapis.com/auth/calendar.readonly'],
        redirect_uri='http://localhost:8000/rest/v1/calendar/redirect/'
    )

    flow.fetch_token(code=code)

    credentials = flow.credentials
    access_token = credentials.token

    if not credentials.valid:
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(requests.Request())

    service = build('calendar', 'v3', credentials=credentials)
    events_result = service.events().list(calendarId='primary', maxResults=10).execute()
    events = events_result.get('items', [])

    event_list = []
    for event in events:
        event_list.append(event['summary'])

    return HttpResponse(', '.join(event_list))
