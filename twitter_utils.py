import tweepy
import os, random
from models import *

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

# Get a representation of the User who has logged in.
# Also, get a list of 100 recent friends which we can store for creating
# timelines for questions later:
def getDetails(session):
    api = getAuthenticatedAPI(session)
    user = api.verify_credentials()
    friend_ids = api.friends_ids(user_id=user.id,count=100)
    user.friends = api.lookup_users(user_ids=friend_ids)
    return user

# Get the authenticated user's home timeline (Tweets from self and friends)
def getHomeTimeline(session):
    api = getAuthenticatedAPI(session)
    timeline = api.home_timeline()
    return timeline

def getUserTimeline(session, user):
    api = getAuthenticatedAPI(session)
    timeline = api.user_timeline(id=user.id)
    return timeline


## UTILITY METHODS  ##

# Return a randomly chosen friend using roulette wheel selection.
# Selection is weighted towards users at the START of the list.
# Used for selecting a friend of the user for displaying the timeline
# in a question:
def getWeightedChoice(friends):
    choices = []
    weight = len(friends) # initial start weight
    for friend in friends:
        choices.append((friend, weight))
        weight = weight - 1
    
    # Now do weighted selection:
    total = sum(w for c, w in choices)
    r = random.uniform(0, total)
    upto = 0
    for c, w in choices:
        if upto + w > r:
            return c
        upto += w
    assert False, "Shouldn't get here"


# Return the timeline for the specified question
def getTimelineForQuestion(question, session, user):
    mostFollowersFirst = sorted(user.friends, key=lambda user: user.followers_count)
    timeline = None
    if question == 1:
        timeline = getHomeTimeline(session)
    elif question == 2:
        friend = mostFollowersFirst[-1]
        timeline = getUserTimeline(session, friend)
    elif question == 3:
        friend = getWeightedChoice(mostFollowersFirst)
        timeline = getUserTimeline(session, friend)
    elif question == 4:
        friend = mostFollowersFirst[-2]
        timeline = getUserTimeline(session, friend)
    elif question == 5:
        friend = getWeightedChoice(mostFollowersFirst)
        timeline = getUserTimeline(session, friend)
    elif question == 6:
        friend = getWeightedChoice(mostFollowersFirst)
        timeline = getUserTimeline(session, friend)

    return timeline

def getQuestionCount():
    return 6

def getDescriptionForQuestion(question):
    if question == 1:
        return "This question contains Tweets from your 'home timeline'. This is the timeline you'd see if you were logged into Twitter right now, so it contains Tweets from several different users."
    if question >= 2:
        return "This timeline contains Tweets from only one of your Twitter friends."
