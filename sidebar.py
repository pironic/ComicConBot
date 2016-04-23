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
			print venue_string
			
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
	r = praw.Reddit("Comic Convention Sidebar Updater")
	r.set_oauth_app_info(cfg.oauth_client_id,
						cfg.oauth_client_secret,
						cfg.oauth_redirect_uri)
	# url = r.get_authorize_url('comicconbot', 'identity edit modconfig modflair wikiedit wikiread', True)
	# print url

	# access_information = r.get_access_information(cfg.oauth_auth_code)
	# print access_information["refresh_token"]

	access_information = r.refresh_access_information(cfg.oauth_refresh_token)
	r.set_access_credentials(**access_information)
	authenticated_user = r.get_me()
	print "Logged in as " + authenticated_user.name, authenticated_user.link_karma

	for subreddit in cfg.subreddits:

		print "Start r/"+subreddit
		s = r.get_subreddit(subreddit)

		try:
			config = HTMLParser.HTMLParser().unescape(r.get_wiki_page(s,"config/sidebar").content_md)
		except requests.exceptions.HTTPError:
			print "Couldn't access format wiki page, reddit may be down."
			raise
			
		print "Checking if sidebar needs updating..."
		sidebar = r.get_settings(s)
		submit_text = HTMLParser.HTMLParser().unescape(sidebar["submit_text"])
		desc = HTMLParser.HTMLParser().unescape(sidebar['description'])

		startmarker, endmarker = desc.index("[](#StartMarker)"), desc.index("[](#MarkerEnd)") + len("[](#MarkerEnd)")
		updated_desc = desc.replace(desc[startmarker:endmarker], "[](#StartMarker)\n \n" + sidebar_string + "\n \n[](#MarkerEnd)")

		if updated_desc != desc:
			print "Updating sidebar..."
			s.update_settings(description=updated_desc.encode('utf8'), submit_text=submit_text)
		print "Done r/"+subreddit

	print "Done All"
except praw.errors.InvalidCaptcha:
    pass