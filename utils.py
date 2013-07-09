import tweepy
import os

# Load the application's consumer token and secret from 
# environment variables.
CONSUMER_TOKEN = os.environ.get('twinteresting_token')
CONSUMER_SECRET = os.environ.get('twinteresting_secret')

## AUTHORISATION METHODS ##

# Get the OAuth authorisation URL from Twitter. Users taking
# part in the experiment will be redirected here to authenticate
# with Twitter before being re-sent back to our callback() endpoint.
def getAuthURL():
    auth = tweepy.OAuthHandler(CONSUMER_TOKEN, CONSUMER_SECRET)
    redirect_url = None
    try:
        redirect_url = auth.get_authorization_url()
    except:
        print "Error getting auth URL"
    return (auth, redirect_url)

# Generate the access_token from the verifier sent back from Twitter
# to callback(). This is the final stage of the OAuth authorisation
# and returns the access token key and secret to be stored in the
# user's session.
def getAccessToken(verifier, request_key, request_secret):
    auth = tweepy.OAuthHandler(CONSUMER_TOKEN, CONSUMER_SECRET)
    auth.set_request_token(request_key, request_secret)
    try:
        auth.get_access_token(verifier)
    except:
        print "Error getting access token"
    return (auth.access_token.key, auth.access_token.secret)

# Generate an authenticated API instance with the access_token
# stored in the user's session.
def getAuthenticatedAPI(session):
    key = session['access_key']
    secret = session['access_secret']
    auth = tweepy.OAuthHandler(CONSUMER_TOKEN, CONSUMER_SECRET)
    auth.set_access_token(key, secret)
    return tweepy.API(auth)


## TWITTER API METHODS ##

# Get a representation of the User who has logged in
def getDetails(session):
    api = getAuthenticatedAPI(session)
    user = api.verify_credentials()
    return user


## UTILITY METHODS AND CLASSES ##

# Create and return a User object based on the details stored in
# the user's session variables.
def generateUserFromSession(session):
    name = session['name']
    screen_name = session['screen_name']
    profile_image = session['profile_image']
    friends_count = session['friends_count']
    user = User(name, screen_name, profile_image, friends_count)
    return user


# Own implementation of User object containing only the information 
# we need. friends_count stored as the experiment will not work if 
# user has 0 friends.
class User:
    def __init__(self, name, screen_name, profile_image, friends_count):
        self.name = name
        self.screen_name = screen_name
        self.profile_image = profile_image
        self.friends_count = friends_count 