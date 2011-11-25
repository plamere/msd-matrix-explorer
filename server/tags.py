import sys
import os
import re
import math
import ds
import track as track_info
import simplejson as json
import collections



tag_file = '/lab/mir/data/msd/track_tags.dat'
tag_file = '../../track_tags_tiny.dat'


valid_tags = set()
artist_tags = collections.defaultdict(dict)

def normalize(word):    
    word = re.sub(r'[\W+]', ' ', word)
    word = re.sub(r'\s+', ' ', word)
    return word.lower().strip()


def dump_dict(title, dict, count=1000):
    list = [ (c,tag) for tag, c in dict.items()]
    list.sort(reverse=True)
    print '===', title, '==='
    for c, tag in list[:count]:
        print c, tag

def dump_tag_tracks():
    for i, (k, l) in enumerate(tag_tracks.items()):
        print i, k, len(l)

def get_average_tag_count(tags):
    sum = 0
    total = 0.0
    for tag_count in tags.split(','):
        tc = tag_count.split(':')
        if len(tc) == 2:
            count = int(tc[1])
            sum += count
            total += 1.0
    if total > 0:
        avg = sum / total
    else:
        avg = 0
    return avg

def make_confusion_matrix(top=50, presence_only=False):
    tag_tracks = collections.defaultdict(list)
    matrix = {}

    valid_tags = find_top_tags(top)
    for which, line in enumerate(open(tag_file)):
        tid, sid, artist, title, tags = line.strip().split('<SEP>')
        tags = tags.strip()
        if len(tags) > 0:
            tlist = []
            track = { 'id' : tid, 'artist' : artist, 'title': title, 'tags' : tlist }
            avg_tc = get_average_tag_count(tags)
            nartist = normalize(artist)
            atags = artist_tags[nartist]
            for tag_count in tags.split(','):
                tc = tag_count.split(':')
                if len(tc) == 2:
                    tag = tc[0]
                    if tag in valid_tags:
                        if presence_only:
                            count = 1
                        else:
                            count = int(tc[1])
                        score =  count / avg_tc
                        tlist.append( (tag, score) )
                        tag_tracks[tag].append( (track, score) )
                        if not tag in atags:
                            atags[tag] = score
                        else:
                            atags[tag] += score
                else:
                    print 'tc len', len(tc), tag_count
            for t1,c1 in tlist:
                for t2, c2 in tlist:
                    if t1 not in matrix:
                        matrix[t1] = collections.defaultdict(int)
                    matrix[t1][t2] += c1

    for tag, tracks in tag_tracks.items():
        tracks.sort(reverse=True, key=lambda a : a[1])
        #print 'sort', tag, tracks[:10]

    normalize_matrix(matrix)
    return matrix, tag_tracks

def find_overlapping_keys(tag, matrix, threshold=.03, max=1000):
    tag = normalize(tag)
    keys = []
    if tag in matrix:
        row = matrix[tag]
        for k, ovlp in row.items():
            score = average([ v for k2, v in matrix[k].items()])
            cscore = average( column(matrix, k) )
            # print 'avg', k, tag, score, cscore, ovlp
            rel_threshold = cscore * 3
            if ovlp > threshold and ovlp > rel_threshold:
                keys.append( (ovlp, k))
    keys.sort(reverse=True)
    keys = [ k for ovlp, k in keys ]
    return  keys[:max]

def subset_matrix(keys, matrix):
    new_matrix = {}

    for k1 in keys:
        new_matrix[k1] = {}
        for k2 in keys:
            new_matrix[k1][k2] = matrix[k1][k2]
    return new_matrix

def order_keys(matrix, start):
    remaining_keys = sorted(list(matrix.keys()))
    current_keys = []
    current_score = 0

    key = remaining_keys.remove(start)
    current_keys.append(start)

    while len(remaining_keys) > 0:
        last = current_keys[-1]
        best = -1
        best_key = None
        for key in remaining_keys:
            ovlp = matrix[last][key]
            if ovlp > best:
                best = ovlp
                best_key = key
        current_score += best
        remaining_keys.remove(best_key)
        current_keys.append(best_key)
    return current_score, current_keys

def find_best_key_order(matrix):
    best = 0
    best_keys = None
    for k in sorted(list(matrix.keys())):
        score, keys = order_keys(matrix, k)
        if score > best:
            best = score
            best_keys = keys
    return best_keys
    


def find_top_tags(return_count):
    if len(valid_tags) == return_count:
        return

    valid_tags.clear()
    tag_total = collections.defaultdict(int)

    for which, line in enumerate(open(tag_file)):
        tid, sid, artist, title, tags = line.strip().split('<SEP>')
        tags = tags.strip()
        avg_tc = get_average_tag_count(tags)
        if len(tags) > 0:
            for tag_count in tags.split(','):
                tc = tag_count.split(':')
                if len(tc) == 2:
                    tag = tc[0]
                    count = int(tc[1])
                    tag_total[tag] += count / avg_tc
    list = [ (c,tag) for tag, c in tag_total.items()]
    list.sort(reverse=True)
    for c, tag in list[:return_count]:
        valid_tags.add(tag)
    return valid_tags


def column(matrix, key):
    return [ matrix[k][key] for k in matrix.keys()]

def average(arr):
    return sum(arr) / float(len(arr))

def normalize_matrix(matrix):
    for k1 in matrix.keys():
        row_max = float(max( matrix[k1].values()))
        for k2 in matrix.keys():
            matrix[k1][k2] = matrix[k1][k2] / row_max


def matrix_to_dict(matrix, keys = None):
    threshold = .01

    if keys == None:
        keys = matrix.keys()
    nodes = []
    for k in keys:
        nodes.append( { 'nodeName': k, 'group': 1 } )

    links = []

    for i, r in enumerate(keys):
        for j,c in enumerate(keys):
            val = matrix[r][c]
            if val >= threshold:
                links.append( { 'source' : i, 'target': j, 'value':val } ) 
    graph = { 'nodes' : nodes, 'links' : links }
    return graph

     

def get_confusion_matrix():
    #matrix = store.get('matrix')
    #tag_tracks = store.get('tag_tracks')
    matrix = None
    tag_tracks = None
    if not matrix or not tag_tracks:
        matrix, tag_tracks = make_confusion_matrix(1000, False)
        #store.put('matrix', matrix)
        #store.put('tag_tracks', tag_tracks)
    return matrix, tag_tracks


def load():
    global store, matrix, tag_tracks
    #store = ds.DataStore('cache.db')
    matrix, tag_tracks = get_confusion_matrix()
  
def sort_keys(keys, matrix, sort):
    if sort == 'alpha':
        return sorted(keys)
    elif sort == 'cluster':
        return find_best_key_order(matrix)

    # TODO sort by relevance and popularity
    return keys

def build_tag_graph(tag, max_size, sort):
    graph = None
    tag = normalize(tag)
    if tag in matrix:
        keys = find_overlapping_keys(tag, matrix, max=max_size)
        lmatrix = subset_matrix(keys, matrix)
        keys = sort_keys(keys, lmatrix, sort)
        graph = matrix_to_dict(lmatrix, keys)
    return graph

def build_artist_graph(artist, max_size, sort):
    graph = None
    artist = normalize(artist)
    keys = []
    if artist in artist_tags:
        tags = artist_tags[artist]
        taglist = [ (v,k) for k,v in tags.items() ]
        taglist.sort(reverse=True)
        taglist = taglist[:max_size]
        for v,k in taglist:
            keys.append(k)
        lmatrix = subset_matrix(keys, matrix)
        keys = sort_keys(keys, lmatrix, sort)
        graph = matrix_to_dict(lmatrix, keys)
    return graph

def get_ovlp_score(track, count, tag2):
    for t,c in track['tags']:
        if t == tag2:
            return c * count
    return 0
    
def add_track_info(track): 
    if not 'mp3' in track:
        mp3, img = track_info.get_track_info(track['id'])
        track['mp3'] = mp3
        track['img'] = img
    return 'mp3' in track and len(track['mp3']) > 0


def get_top_results_with_tracks(results, count):
    ret_results = []
    for result in results:
        track, score  = result
        if add_track_info(track):
            ret_results.append(result)
            if len(ret_results) >= count:
                break
    return ret_results
        

def find_top_tracks(tag1, tag2, start, count):
    tag1 = normalize(tag1)
    if tag1 in tag_tracks and tag2 == None:
        results = tag_tracks[tag1]
    else:
        tag2 = normalize(tag2)
        results =  []
        for track, tcount in tag_tracks[tag1]:
            score = get_ovlp_score(track, tcount, tag2)
            if score > 0:
                results.append( (track, score) )
        results.sort(key=lambda tc: tc[1], reverse=True)

    results = get_top_results_with_tracks(results, start + count)
    if start > len(results):
        start = start % len(results)
    return results[start:start + count]
            

if __name__ == '__main__':
    import pprint
    load()

    tag =  sys.argv[1] if len(sys.argv) > 1 else 'heavy metal'
    l =  int(sys.argv[2]) if len(sys.argv) > 2 else 24
    sort =  sys.argv[3] if len(sys.argv) > 3 else 'alpha'

    if False:
        graph = build_tag_graph(tag, l, sort)
        pprint.pprint(graph)
        #dump_tag_tracks()

    if False:
        top_metal = find_top_tracks('metal', 'emo', 10)
        for t,c in top_metal:
            print c, t

    if True:
        graph = build_artist_graph('Korn', l, sort)
        pprint.pprint(graph)
