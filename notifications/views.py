from django.shortcuts import render
import queue
from django.http import StreamingHttpResponse

# Create your views here.

# Global queue to store messages
event_queue = queue.Queue()

def event_stream():
    while True:
        message = event_queue.get()  # Block until a message is available
        yield message


def sse_view(request):
    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    return response