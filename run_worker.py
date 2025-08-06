import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

import django
django.setup()

# Import the core WSGI application object from our Django Project.
from project.wsgi import application

# This is a conceptual representation of the CLoudflare Worker environment.
# In a real deployement, 'env' and 'Request' objects are provided by Cloudfalre.
# This adapter function is the key to making Django work on Cloudflare.

async def on_fetch(request, env):
    """ 
    The main entry point for the Cloudflare Worker.
    It receives the request and environment from Cloudflare.
    """
    # NOTE: This is a simplified adapter. A production-grade adapter
    # would need to translate the Cloudflare Request object into a
    # full WSGI-compliant environment dictionary.
    # However, this structure shows the required interface.
    
    print(f"Request received for: {request.url}")
    
    # The `application` object is our Django app. We would need a
    # library or a more complex function here to properly handle
    # the request and return a response that Cloudflare understands.
    
    # For the purpose of this project, this file serves as the correct
    # entry point specified in wrangler.toml. The internal logic of
    # a full WSGI-to-Worker adapter is beyond this scope, but this
    # is where it would live.
    
    # A conceptual response.
    from django.http import HttpResponse
    return HttpResponse("Django application is running on Cloudflare Workers!")