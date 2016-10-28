"""Bot configuration."""

TEST_ROOM_ID = '580364f3d73408ce4f2e97dc'  # R2-D2 Repair Station
MAIN_ROOM_ID = '54ca0dd2db8155e6700f36e1'  # AfricanPenguin
BOT_NAME = 'CERN-R2-D2'

with open('ACCESS_TOKEN', 'r') as fp:
    ACCESS_TOKEN = fp.read().strip()

# !<command> or @CERN-R2-D2 <command>
CMD_PREFIX = ('!', '@' + BOT_NAME)