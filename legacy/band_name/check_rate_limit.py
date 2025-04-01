import requests
import time
import base64

CLIENT_ID_OLD = '68638f90ae504fc7b4e57953c72bf302'
CLIENT_SECRET_OLD = '0c25a7ea73f2472986dde61c27fc1f57'

CLIENT_SECRET = '9556bff0ffc54cc0bbca64ef79cf93df'
CLIENT_ID = '3ea9f87d635f4d5fa8b509a7b626f08c'

def get_spotify_token(client_id, client_secret):
    try:
        credentials = f"{client_id}:{client_secret}"
        credentials_encoded = base64.b64encode(credentials.encode('ascii')).decode('ascii')
        
        auth_response = requests.post(
            'https://accounts.spotify.com/api/token',
            headers={
                'Authorization': f'Basic {credentials_encoded}'
            },
            data={
                'grant_type': 'client_credentials'
            }
        )
        auth_response_data = auth_response.json()
        return auth_response_data['access_token']
    except Exception as e:
        print(f"Error obtaining Spotify token: {e}")
        return None


def check_rate_limit(token):
    headers = {
        'Authorization': 'Bearer ' + token
    }
    
    # We'll use the search endpoint for this example
    query = 'https://api.spotify.com/v1/search?q=example&type=artist'
    response = requests.get(query, headers=headers)
    
    # Extract rate limit headers
    rate_limit = response.headers.get('X-RateLimit-Limit')
    rate_remaining = response.headers.get('X-RateLimit-Remaining')
    rate_reset = response.headers.get('X-RateLimit-Reset')

    # Print the rate limit information
    print(f"Rate Limit: {rate_limit}")
    print(f"Requests Remaining: {rate_remaining}")
    if rate_reset:
        rate_reset_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(rate_reset)))
        print(f"Rate Reset Time: {rate_reset_time}")

    # Check for rate limit exceeded status code
    if response.status_code == 429:
        retry_after = int(response.headers.get('Retry-After', 0))
        print(f"Rate limited! Please wait for {retry_after} seconds.")
    
if __name__ == "__main__":
    token = get_spotify_token(CLIENT_ID, CLIENT_SECRET)
    if token:
        check_rate_limit(token)
    else:
        print("Failed to obtain token.")
