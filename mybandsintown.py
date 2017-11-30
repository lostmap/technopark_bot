import telega

from bandsintown import Client
# Instantiate client with your app id (this can be anything)
client = Client('technopark_ruliiiit')

pushpin = u'\U0001F4CC' #pushpin emoji

def create_message(events): 
    messages = list() #массив сообщений
    if events:
        message = {'artist_id': 0, 'text': '', 'photo': ''}

        if events[0]['artists'][0]['name']:
                message['text'] += "Artist: " + events[0]['artists'][0]['name'] + "\n\n"
        
        message['artist_id'] += events[0]['artist_id'] 
        message['photo'] += "[" + pushpin + "](" + events[0]['artists'][0]['thumb_url'] + ")"
        clock = 0
        for event in events:
            clock += 1
            message['text'] += "*" + event['title'] + "* \n"
            message['text'] += "Event date: " + event['formatted_datetime'] + "\n"
             
            if event['ticket_url']:
                message['text'] += "[By tickets](" + event['ticket_url'] + ")\n\n"
            else:
                message['text'] += "[By tickets](" + events[0]['facebook_rsvp_url'] + ")\n\n"
            if clock == 5: #каждые 5 событий = новое сообщение
                messages.append(message)
                message = {'artist_id': 0, 'text': '', 'photo': ''}
                if events[0]['artists'][0]['name']:
                    message['text'] += "Artist: " + event['artists'][0]['name'] + "\n\n"
                clock = 0
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
