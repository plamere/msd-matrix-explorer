
import simplejson as json
import urllib2
import sys
import pprint

url = 'http://developer.echonest.com/api/v4/track/profile?api_key=EHY4JJEGIOFA1RCJP&id='

def get_track_info(id):
    full_url = url  + id
    try:
        print 'gti', id
        connection = urllib2.urlopen(full_url)
        jresponse = connection.read()
        connection.close()
        response = json.loads(jresponse)
        track = response['response']['track']

        if track:
            return track['preview_url'], track['release_image']
    except:
        print 'error'
        return "", ""

    return "", ""



if __name__ == '__main__':
    mp3, img = get_track_info(sys.argv[1])
    print 'mp3',mp3
    print 'img',img

