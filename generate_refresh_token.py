"""Generates refresh token for AdWords using the Installed Application flow."""


import argparse
import sys

from oauth2client import client

# Your OAuth2 Client ID and Secret. If you do not have an ID and Secret yet,
# please go to https://console.developers.google.com and create a set.
DEFAULT_CLIENT_ID = "912158577730-gp482m9nn7bd3t9hfl1od6k4bqcu70fp.apps.googleusercontent.com"

DEFAULT_CLIENT_SECRET = "UCNb8ERVGx2NUwwBFxj7UQt1"

# The AdWords API OAuth2 scope.
SCOPE = u'https://www.googleapis.com/auth/adwords'

parser = argparse.ArgumentParser(description='Generates a refresh token with '
                                 'the provided credentials.')
parser.add_argument('--client_id', default=DEFAULT_CLIENT_ID,
                    help='Client Id retrieved from the Developer\'s Console.')
parser.add_argument('--client_secret', default=DEFAULT_CLIENT_SECRET,
                    help='Client Secret retrieved from the Developer\'s '
                    'Console.')
parser.add_argument('--additional_scopes', default=None,
                    help='Additional scopes to apply when generating the '
                    'refresh token. Each scope should be separated by a comma.')


def main(client_id, client_secret, scopes):
  """Retrieve and display the access and refresh token."""
  flow = client.OAuth2WebServerFlow(
      client_id=client_id,
      client_secret=client_secret,
      scope=scopes,
      user_agent='Ads Python Client Library',
      redirect_uri='urn:ietf:wg:oauth:2.0:oob')

  authorize_url = flow.step1_get_authorize_url()

  print ('Log into the Google Account you use to access your AdWords account'
         'and go to the following URL: \n%s\n' % (authorize_url))
  print 'After approving the token enter the verification code (if specified).'
  code = raw_input('Code: ').strip()

  try:
    credential = flow.step2_exchange(code)
  except client.FlowExchangeError, e:
    print 'Authentication has failed: %s' % e
    sys.exit(1)
  else:
    print ('OAuth2 authorization successful!\n\n'
           'Your access token is:\n %s\n\nYour refresh token is:\n %s'
           % (credential.access_token, credential.refresh_token))


if __name__ == '__main__':
  args = parser.parse_args()
  configured_scopes = [SCOPE]
  if not (any([args.client_id, DEFAULT_CLIENT_ID]) and
          any([args.client_secret, DEFAULT_CLIENT_SECRET])):
    raise AttributeError('No client_id or client_secret specified.')
  if args.additional_scopes:
    configured_scopes.extend(args.additional_scopes.replace(' ', '').split(','))
  main(args.client_id, args.client_secret, configured_scopes)