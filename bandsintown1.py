# Instantiate client with your app id (this can be anything)

import telega

from bandsintown import Client
client = Client('technopark_ruliiiit')




# #GET
#
# # Find an artist by name
#
# client.get('Bad Religion')
#
# # Find an artist by Facebook page ID
#
# client.get(fbid=168803467003)
#
# # Find an artist by MusicBrainz ID
#
# client.get(mbid='149e6720-4e4a-41a4-afca-6d29083fc091')
#
#
#
# #Events
#
# client.events('Bad Religion')
#
# # Filter by date
#
# client.events('Bad Religion', date='2015-08-30')
#
# # ...or a date range
#
# # Filter by date
#
# client.events('Bad Religion', date='2015-08-30,2015-12-25')




#Search



def create_message(events):

    messages = list()
    if events:
        message = ''
        prev_event_title = ''

        if events[0]['artists'][0]['name']:
                message += "Artist: " + events[0]['artists'][0]['name'] + "\n\n"

        for event in events:

            if event['title'] != prev_event_title:
                messages.append(message)
                message = "<b>        " + event['title'] + "</b>\n\n"

            message += "Event date: " + event['formatted_datetime'] + "\n"

            prev_event_title = event['title']

            if event['ticket_url']:
                message += "<a href = \"" + event['ticket_url'] + "\" >By tickets</a>" + "\n\n"
            else:
                message += "<a href = \"" + events[0]['facebook_rsvp_url'] + "\" >By tickets</a>" + "\n\n"

            # "Ticket status: "+ event['ticket_status']
            # "Ticket type: ", event['ticket_type']
            # "Datetime: "+ event['datetime']
            #  "Formatted location: ", event['formatted_datetime']
            # print("Ticket status: ", event['ticket_status'])
            #     print("Facebook page: ", artist['facebook_page_url'])
            #     print("Url: ", artist['url'])
            #     print("Thumb url: ", artist['thumb_url'])
            #     print("Image url: ", artist["image_url"])
            #     print("Facebook tour dates: ", artist['facebook_tour_dates_url'])
            #     print("Website: ", artist['website'])
            #
            # venue = event['venue']
            # print("City: ", venue['city'])
            # print("Name: ", venue['name'])
            # print("Place: ", venue['place'])
            # print("Region: ", venue['region'])

        messages.append(message)

    return messages



# Pass an optional radius (in miles)
#
# client.search('Bad Religion', location='Portland,OR', radius=100)
#

#Recomended
# events = client.recommended('Thirty Seconds to Mars', location='Moscow, Ru')
#
# for event in events:
#     print("Title: ", event['title'])
#     print("Ticket status: ", event['ticket_status'])
#     print("Facebook: ", event['facebook_rsvp_url'])
#     print("Ticket type: ", event['ticket_type'])
#     print("Formated datetime: ", event['formatted_datetime'])
#     print("Datetime: ", event['datetime'])
#     print("Formatted location: ", event['formatted_datetime'])
#     print("Ticket url: ", event['ticket_url'])
#     print("Ticket status: ", event['ticket_status'])
#     for artist in event['artists']:
#         print("Artist: ", artist['name'])
#         print("Facebook page: ", artist['facebook_page_url'])
#         print("Url: ", artist['url'])
#         print("Thumb url: ", artist['thumb_url'])
#         print("Image url: ", artist["image_url"])
#         print("Facebook tour dates: ", artist['facebook_tour_dates_url'])
#         print("Website: ", artist['website'])
#
#     venue = event['venue']
#     print("City: ", venue['city'])
#     print("Name: ", venue['name'])
#     print("Place: ", venue['place'])
#     print("Region: ", venue['region'])


#  Only show recommendations
#
# client.recommended('Rise Against', location='Portland,OR', only_recs=True)
#
