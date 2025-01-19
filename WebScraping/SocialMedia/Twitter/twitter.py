import asyncio
from twikit import Client
import json
import pandas as pd

async def client():
    client = Client('en-US')

    ## You can comment this `login`` part out after the first time you run the script (and you have the `cookies.json`` file)
    '''await client.login(
        auth_info_1='username',
        password='password',
    )

    client.save_cookies('cookies.json')'''
    client.load_cookies(path='cookies.json')

    user = await client.get_user_by_screen_name('amerix')
    tweets = await user.get_tweets('Tweets', count=5)

    tweets_to_store = []

    for tweet in tweets:
        tweets_to_store.append({
            'created_at': tweet.created_at,
            'favorite_count': tweet.favorite_count,
            'full_text': tweet.full_text,
        })
 
    # We can make the data into a pandas dataframe and store it as a CSV file
    df = pd.DataFrame(tweets_to_store)
    df.to_csv('tweets.csv', index=False)

    # Pandas also allows us to sort or filter the data
    print(df.sort_values(by='favorite_count', ascending=False))

    # We can also print the data as a JSON object
    print(json.dumps(tweets_to_store, indent=4))



asyncio.run(client())