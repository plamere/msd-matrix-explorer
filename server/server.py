import os 
import cherrypy
import ConfigParser
import urllib2
import simplejson as json
import tags

class TagServer(object):
    def __init__(self, config):
        self.production_mode = config.getboolean('settings', 'production')
        tags.load()

    # sort can be 'alpha', 'cluster', 'relevance', 'popularity'

    def tag_graph(self, tag="", max_size="24", sort="alpha", _="", callback=None):
        if callback:
            cherrypy.response.headers['Content-Type']= 'text/javascript'
        else:
            cherrypy.response.headers['Content-Type']= 'application/json'

        max_size = int(max_size)
        graph = tags.build_tag_graph(tag, max_size, sort)
        status = 'ok' if graph else 'error'
        results = { 'status': status, 'graph' : graph}
        return to_json(results, callback)
    tag_graph.exposed = True

    def artist_graph(self, artist="", max_size="24", sort="alpha", _="", callback=None):
        if callback:
            cherrypy.response.headers['Content-Type']= 'text/javascript'
        else:
            cherrypy.response.headers['Content-Type']= 'application/json'

        max_size = int(max_size)
        graph = tags.build_artist_graph(artist, max_size, sort)
        status = 'ok' if graph else 'error'
        results = { 'status': status, 'graph' : graph}
        return to_json(results, callback)
    artist_graph.exposed = True

    def top_tracks(self, tag1="", tag2="", start="0", count="24", _="", callback=None):
        if callback:
            cherrypy.response.headers['Content-Type']= 'text/javascript'
        else:
            cherrypy.response.headers['Content-Type']= 'application/json'

        tracks = []
        start = int(start)
        count = int(count)

        if len(tag1) > 0 and len(tag2) > 0:
            tracks = tags.find_top_tracks(tag1, tag2, start,count)
            status = "ok"
        elif len(tag1) > 0:
            tracks = tags.find_top_tracks(tag1, None, start, count)
            status = 'ok'
        else:
            status = 'no tag'

        results = { 'status': status, 'tracks' : tracks}

        return to_json(results, callback)
    top_tracks.exposed = True


def to_json(dict, callback=None):
    results =  json.dumps(dict, sort_keys=True, indent = 4) 
    if callback:
        results = callback + "(" + results + ")"
    return results

if __name__ == '__main__':
    urllib2.install_opener(urllib2.build_opener())
    conf_path = os.path.abspath('web.conf')
    print 'reading config from', conf_path
    cherrypy.config.update(conf_path)

    config = ConfigParser.ConfigParser()
    config.read(conf_path)
    production_mode = config.getboolean('settings', 'production')

    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Set up site-wide config first so we get a log if errors occur.

    if production_mode:
        print "Starting in production mode"
        cherrypy.config.update({'environment': 'production',
                                'log.error_file': 'simdemo.log',
                                'log.screen': True})
    else:
        print "Starting in development mode"
        cherrypy.config.update({'noenvironment': 'production',
                                'log.error_file': 'site.log',
                                'log.screen': True})

    cherrypy.quickstart(TagServer(config), '/TagServer')

