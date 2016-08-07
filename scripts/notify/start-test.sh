#!/bin/bash

set -e

ICON_URL="https://dl.dropboxusercontent.com/u/29279948/Slack/Icons/CircleCI.png"

curl -XPOST \
    -d "token=$SLACK_API_TOKEN" \
    -d "channel=emoji" \
    -d "text=start   test   \`Emoji-Web\` *$CIRCLE_BRANCH* by CircleCI" \
    -d "username=CircleCI" \
    -d "icon_url=$ICON_URL" \
    "https://slack.com/api/chat.postMessage"
