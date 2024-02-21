from django.shortcuts import render , redirect , HttpResponseRedirect
from django.views import View

# Create your views here.
    
def privacy_policy(request): 

    data = {}

    print('you are viewing: ', 'privacy policy')
    return render(request, 'privacy-policy.html', data)
    
def terms_conditions(request): 

    data = {}

    print('you are viewing: ', 'terms conditions')
    return render(request, 'terms-conditions.html', data)


