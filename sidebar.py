import requests
import feedparser
import praw
import HTMLParser
import config as cfg
# import time

print "Fetching Comic Feed..."
feed = feedparser.parse( cfg.rss_url )
print "Building Convention list..."
nextcons = []
# firstdate = time.strftime(""%m/%d/%y")
firstdate = "0"
for item in feed["items"]:
	title = item["title"]
	if title[:5] == "Comic":
		if firstdate == "0":
			firstdate = title[-8:]
		# print item["description"]
		if title[-8:] == firstdate or len(nextcons) < cfg.cons_to_show:
			deets = title[21:]
			venue = item["description"].split("<strong>Venue:</strong>")[1].split("</a>")[0]
			# print title
			venue_name = venue.split(">")[1]
			venue_link = venue.split("\"")[1]
			venue_string = "["+venue_name+"]("+venue_link+")" + deets
			print venue_string.encode('utf-8')
			
			nextcons.append(venue_string)

sidebar_string = ""#"**Next "+str(cfg.cons_to_show)+" ComicCons**"
condate = "0"
for con in nextcons:
	con_title = con.split(" on ")[0]
	con_date = con.split(" on ")[1]
	if condate != con_date:
		condate = con_date
		sidebar_string += "\n\n**Conventions on " + condate + "**"
	sidebar_string += "\n\n* " + con_title

sidebar_string += "\n\nFor complete listing you can check [conventionscene.com]("+feed["channel"]["link"]+")"

try: 
	print "Logging in..."
	r = praw.Reddit(user_agent="Comic Convention Sidebar Updater",
		client_id=cfg.oauth_client_id,
		client_secret=cfg.oauth_client_secret,
		username=cfg.username,
		password=cfg.password)
	print "DEBUG: oauth sent"

	# url = r.get_authorize_url('comicconbot', 'identity edit modconfig modflair wikiedit wikiread', True)
	# print url

	# access_information = r.get_access_information(cfg.oauth_auth_code)
	# print access_information["refresh_token"]

	authenticated_user = r.user.me()
	print "Logged in as " + authenticated_user.name, authenticated_user.link_karma

	for subreddit in cfg.subreddits:

		print "Start r/"+subreddit
		s = r.subreddit(subreddit)
		w = s.wiki["config/sidebar"]

		try:
			desc = HTMLParser.HTMLParser().unescape(w.content_md)
		except requests.exceptions.HTTPError:
			print "Couldn't access format wiki page, reddit may be down."
			raise

		print "Checking if sidebar needs updating..."
		startmarker, endmarker = desc.index("[](#StartMarker)"), desc.index("[](#MarkerEnd)") + len("[](#MarkerEnd)")
		updated_desc = desc.replace(desc[startmarker:endmarker], "[](#StartMarker)\n \n" + sidebar_string + "\n \n[](#MarkerEnd)")

		if updated_desc != desc:
			print "Updating sidebar..."
			w.edit(updated_desc, reason="/u/ComicConBot Scheduled Update")
		print "Done r/"+subreddit

	print "Done All"
except praw.exceptions.APIException:
    pass
