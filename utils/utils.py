class utils:
    def rangeCorrector(ranges):
        if ([0, 99] not in ranges):
            ranges.insert(0, [0, 99])
        return ranges

    def getRanges(index, multiplier, memberCount):
        initialNum = int(index*multiplier)
        rangesList = [[initialNum, initialNum + 99]]
        if (memberCount > initialNum + 99):
            rangesList.append([initialNum + 100, initialNum + 199])
        return utils.rangeCorrector(rangesList)

    def parseGuildMemberListUpdate(response):
        memberdata = {
            "online_count": response["d"]["online_count"],
            "member_count": response["d"]["member_count"],
            "id": response["d"]["id"],
            "guild_id": response["d"]["guild_id"],
            "hoisted_roles": response["d"]["groups"],
            "types": [],
            "locations": [],
            "updates": []
        }

        for chunk in response['d']['ops']:
            memberdata['types'].append(chunk['op'])
            if (chunk['op'] in ('SYNC', 'INVALIDATE')):
                memberdata['locations'].append(chunk['range'])
                if (chunk['op'] == 'SYNC'):
                    memberdata['updates'].append(chunk['items'])
                else:
                    memberdata['updates'].append([])
            elif (chunk['op'] in ('INSERT', 'UPDATE', 'DELETE')):
                memberdata['locations'].append(chunk['index'])
                if (chunk['op'] == 'DELETE'):
                    memberdata['updates'].append([])
                else:
                    memberdata['updates'].append(chunk['item'])

        return memberdata