# googlebot
simple python script to run a google gemini bot for your discord server

# how to run
```
pip install -r requirements.txt
python3 main.py
```

# features
- replies to discord messages with output from google's gemini API
- google search built in due to using vertex ai!
- verbose logging, including each message's discord userID and username
- response status updates that are edited in the discord reply

# requirements
- google cloud credentials json as ./auth.json + cloud project created + funded account - https://cloud.google.com/docs/authentication/application-default-credentials
- discord API key + the bot account created and invited to your server(s)
- python 3.8 or higher

# config notes
- you can change the model but gemini-1.5-pro (the default) is the best - https://ai.google.dev/gemini-api/docs/models/gemini
- you can change the max input and output tokens if you want to spend more or less money
- you can change the google cloud location but I just use their default
- changing or removing the system prompt will impact the output - notably, if you remove the part about the tags, it will print those with every reponse

# extra notes
- rarely, the script misses a message (I blame discord). this is why I added the status updates. if you don't immediately get a reply, the script never saw the message. if it hangs on the third status update, it probably got blocked by the google AI safety filter
- this script was based on the claudebot script that I made with claude 3 opus - [shugy0/claudebot](https://github.com/shugy0/claudebot)
- tiktoken is the fastest token counter, so even though it's using openai's tokenizer, it's close enough
- I run mine on aws lightsail, but you can run yours locally or whatever
- sometimes it throws exceptions but it keeps working anyways lol
