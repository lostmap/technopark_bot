# Instantiate client with your app id (this can be anything)

import telega

from bandsintown import Client
client = Client('technopark_ruliiiit')


def create_message(events):

    messages = list()
    print(events)
    for event in events:
        message = list()
        # + "Ticket status: "+ event['ticket_status'] + "\n"
        # print("Ticket type: ", event['ticket_type'])
        message.append("Event date: " + event['formatted_datetime'])
        # message += "Datetime: "+ event['datetime']
        # print("Formatted location: ", event['formatted_datetime'])
        if (event['ticket_url']):
            message.append("Ticket url: " + event['ticket_url'])
        # print("Ticket status: ", event['ticket_status'])
        for artist in event['artists']:
            if (artist['name']):
                message.append("Artist: "+ artist['name'])
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
        messages.append("\n".join(message))
    messages.append("Title: " + event['title'] + "\n" + event['facebook_rsvp_url'])
    return messages


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

