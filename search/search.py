import pysolr
from flask import request, make_response, render_template
from flask_restful import Resource
import flask_login
from etherpad_cached_api import listPads, getLastEdited, getText, humanPadName

import settings

# Create a client instance.
solr = pysolr.Solr('http://localhost:8983/solr/pw/', always_commit=True)


# Update a single group
def updateIndex(groupId):
    # get pads in solr
    sPads = solr.search('group:{0}'.format(groupId), **{
        'fl': 'id,lastmod'
    })

    timestamps = {}
    for pad in sPads:  # solr fucks with our date formatting
        timestamps[pad['id']] = pad['lastmod'][0][:16]
        timestamps[pad['id']].replace('T', ' ')

    # check which ones need to be updated
    queue = []
    for pad in listPads(groupId):
        if pad in timestamps.keys() and timestamps[pad]:
            continue

        queue.append(pad)

    # Build update Query
    sQuery = []
    for pad in queue:
        sQuery.append({
            'id': pad,
            'group': groupId,
            'content': getText(pad),
            'lastmod': getLastEdited(pad)
        })

    # execute query if not empty
    if sQuery:
        solr.add(sQuery)


# updateIndex('g.sDzoMmut4DIOgrip')
class Search(Resource):
    @flask_login.login_required
    def get(self):

        results = solr.search('id:*IT* + content:Daniel', **{
            'fq': 'group:g.sDzoMmut4DIOgrip',
            'fl': 'id,lastmod',
            'hl': 'true',
            # 'hl.fragsize': 10,
            'hl.fl': 'content',
            'hl.requireFieldMatch': "true"
        })

        hl = results.highlighting

        resp = []
        for result in results:
            r = {
                'id': result['id'],
                'title': humanPadName(result['id']),
                'lastmod': result['lastmod'][0],
                'url': settings.data['pad']['url'] + result['id']
            }

            if result['id'] in hl.keys() and 'content' in hl[result['id']].keys():
                r['content'] = '...'.join(hl[result['id']]['content'])

            resp.append(r)

        return resp


class View(Resource):
    @flask_login.login_required
    def get(self):
        # get selected tab
        active_group = request.args.get('group')

        # default group
        if active_group is None:
            active_group = settings.getDefaultGroup(flask_login.current_user.id,
                    flask_login.current_user.groups)

        # Check if user is allowed to view this group
        viewableGroups = settings.getPadGroups(flask_login.current_user.id,
                flask_login.current_user.groups)

        groupExistsAndAllowed = active_group in viewableGroups


        response = make_response(
            render_template('search.html',
                            groups=viewableGroups,
                            active_group=active_group,
                            groupExistsAndAllowed=groupExistsAndAllowed))
        return response
