import spotipy
import requests
import urllib3
import unidecode
import cmd

from bs4 import BeautifulSoup
from colorama import Fore, init

urllib3.disable_warnings()

init(autoreset=True)


USERNAME = "your username"
SPOTIPY_CLIENT_ID = "your client ID"
SPOTIPY_CLIENT_SECRET = "your client secret"
SPOTIPY_REDIRECT_URI = "http://localhost:8000/"


sources = [
    {
        "url": "https://www.letras.mus.br/{}/{}/traducao.html",
        "html_element": "cnt-trad_l",#"html_element": "cnt-letra"
        "html_element_translate": "cnt-trad_r"
    },
    {
        "url": "https://genius.com/{}-{}-lyrics",
        "html_element": "lyrics",
        "html_element_translate": ""
    }
]


scope = 'user-read-playback-state ' \
        'user-modify-playback-state ' \
        'user-read-currently-playing ' \
        'app-remote-control ' \
        'user-read-private ' \
        'playlist-read-private ' \
        'user-library-read ' \
        'user-read-recently-played '


def getToken():
    token = spotipy.util.prompt_for_user_token(
        USERNAME, scope, client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI)
    return token


def getCurrently_Playing():
    token = getToken()
    if token:
        # Create a Spotify() instance with our token
        sp = spotipy.Spotify(auth=token)
        # method currently playing return an actual song on Spotify
        current_song = sp.currently_playing()
        if current_song is not None:
            # Extract artist from json response
            artist = current_song['item']['artists'][0]['name']
            # Extract song name from json response
            song_name = current_song['item']['name']

            #print('\nSong: {}\nArtist: {}'.format(song_name, artist))

            return {
                        'artist': artist,
                        'song_name': song_name
                    }

        else:
            return 'No music is playing'

    else:
        return 'Can\'t get token for' + USERNAME


def getLyric(artist, song_name):
    found_lyric = False

    token = getToken()
    if token:
        for value in sources:
            if found_lyric != True:
                print('\nsource ' + f'{value["url"]}')

                artist = unidecode.unidecode(str(artist).strip().replace(' ', '-').replace('\'', '')).replace('.', '').replace('/', '-')#.replace('ö', 'o').replace('ü', 'u')
                song_name = unidecode.unidecode(str(song_name).strip().replace(' ', '-').replace('\'', '').replace('(', '').replace(')', '').replace('.', '')).replace('!', '')

                # New request using song_url created before
                request = requests.get(f'{value["url"]}'.format(artist, song_name), verify=False)#request = requests.get("https://genius.com/{}".format(song_url))
                print(f'{value["url"]}'.format(artist, song_name) + '\n')

                # Verify status_code of request
                if request.status_code == 200:
                    # BeautifulSoup library return an html code
                    html_code = BeautifulSoup(request.text, features="html.parser")
                    # Extract lyrics from beautifulsoup response using the correct prefix {"class": "lyrics"}
                    headline = html_code.find("div", {"class": value['html_element']})#headline = html_code.find("div", {"class": "lyrics"})
                    if value['html_element_translate'] != "":
                        headlinetranslate = html_code.find("div", {"class": value['html_element_translate']})

                    if headline is not None:
                        # if "lyrics"
                        #print(headline.get_text())
                        """# if "cnt-letra"
                        lyr = str(headline.prettify()).replace('\n', '').replace('<div class="cnt-letra p402_premium">', '').replace('</div>', '')\
                                .replace('<br/>', '\n').replace('<br>', '\n').replace('</br>', '').replace('<p>', '\n\n').replace('</p>', '')\
                                .replace('   ', '').replace('  ', '')
                        print('\n' + lyr + '\n')"""

                        lyr = (headline.prettify()).split('<span>')
                        lyr_translate = (headlinetranslate.prettify()).split('<span>')
                        for i, lines in enumerate(lyr):
                            lines = str(lines).replace('\n', '').replace('<div class="cnt-trad_l">', '').replace('<h3>', '').replace('</h3>', '\n')\
                                            .replace('</span>', '\n').replace('<p>', '').replace('</p>', '').replace('<br/>', '').replace('</br>', '')\
                                            .replace('<br>', '').replace('</div>', '')\
                                            .replace('    ', '').replace('   ', '').replace('  ', '')

                            lyr_translate[i] = str(lyr_translate[i]).replace('\n', '').replace('<div class="cnt-trad_r">', '').replace('<h3>', '').replace('</h3>', '\n')\
                                            .replace('</span>', '').replace('<p>', '').replace('</p>', '\n').replace('<br/>', '').replace('</br>', '')\
                                            .replace('</div>', '').replace('   ', ' ')#.replace('    ', '')#.replace('   ', '').replace('  ', '')

                            print(lines, Fore.LIGHTBLACK_EX + lyr_translate[i])

                        found_lyric = True
                    else:
                        getLyric(artist, song_name)
                        found_lyric = False

                else:
                    print("\nSorry, I can't find the actual song")

    else:
        return 'Can\'t get token for' + USERNAME


def getDevices():
    token = getToken()
    if token:
        sp = spotipy.Spotify(auth=token)
        devices = sp.devices()
        deviceID = devices['devices'][0]
        return deviceID
    else:
        return "Can't get token for", USERNAME


def getRecentlyPlayed(limit = 2):
    token = getToken()
    if token:
        # Create a Spotify() instance with our token
        sp = spotipy.Spotify(auth=token)
        # method currently playing return an actual song on Spotify
        recently_played = sp.current_user_recently_played(limit=limit)
        if recently_played is not None:
            #print(json.dumps(recently_played, indent=4))
            for item in recently_played['items']:
                print(item['track']['artists'][0]['name'], ' - ', item['track']['name'])
    else:
        return "Can't get token for", USERNAME


def getPlay():
    token = getToken()
    if token:
        # Create a Spotify() instance with our token
        sp = spotipy.Spotify(auth=token)
        # method currently playing return an actual song on Spotify
        start = sp.start_playback()
        if start is not None:
            print(start)
    else:
        return "Can't get token for", USERNAME


def getPause():
    token = getToken()
    if token:
        # Create a Spotify() instance with our token
        sp = spotipy.Spotify(auth=token)
        # method currently playing return an actual song on Spotify
        pause = sp.pause_playback()
        if pause is not None:
            print(pause)
    else:
        return "Can't get token for", USERNAME


def getNext():
    token = getToken()
    if token:
        # Create a Spotify() instance with our token
        sp = spotipy.Spotify(auth=token)
        # method currently playing return an actual song on Spotify
        next = sp.next_track()
        if next is not None:
            print(next)
    else:
        return "Can't get token for", USERNAME


def getPreviousTrack():
    token = getToken()
    if token:
        # Create a Spotify() instance with our token
        sp = spotipy.Spotify(auth=token)
        # method currently playing return an actual song on Spotify
        previous = sp.previous_track()
        if previous is not None:
            print(previous)
    else:
        return "Can't get token for", USERNAME



class TurtleShell(cmd.Cmd):
    intro = 'Welcome to the turtle shell.   Type help or ? to list commands.\n'
    prompt = '(turtle) '
    file = None

    # ----- basic turtle commands -----
    def do_lyric(self, arg):
        'LYRIC or LYRIC [name artist] - [name song]'
        current = {
            'artist': '',
            'song_name': ''
        }
        if arg == '':
            current = getCurrently_Playing()
            print('\nSong: {}\nArtist: {}'.format(current['song_name'], current['artist']))
        else:
            arg = arg.split('-')
            current['artist'] = arg[0].strip()
            current['song_name'] = arg[1].strip()

        getLyric(current['artist'], current['song_name'])
    def do_play(self, arg):
        'PLAY'
        getPlay()
    def do_pause(self, arg):
        'PAUSE'
        getPause()
    def do_next(self, arg):
        'NEXT'
        getNext()
        current = getCurrently_Playing()
        print('\nSong: {}\nArtist: {}\n'.format(current['song_name'], current['artist']))
    def do_previous(self, arg):
        'PREVIOUS'
        getPreviousTrack()
    def do_current(self, arg):
        'CURRENT'
        current = getCurrently_Playing()
        print('\nSong: {}\nArtist: {}\n'.format(current['song_name'], current['artist']))
    def do_devices(self, arg):
        'DEVICES'
        devices = getDevices()
        print(devices)
    def do_recent(self, arg):
        'RECENT or RECENT [limit = 2]'
        if arg:
            getRecentlyPlayed(arg)
        else:
            getRecentlyPlayed()
    def do_exit(self, arg):
        'Stop recording, close the turtle window, and exit:  EXIT'
        print('Thank you for using Turtle')
        self.close()
        return True

    # ----- record and playback -----
    def precmd(self, line):
        line = line.lower()
        if self.file and 'playback' not in line:
            print(line, file=self.file)
        return line
    def emptyline(self):
        return False
    def close(self):
        if self.file:
            self.file.close()
            self.file = None

def parse(arg):
    'Convert a series of zero or more numbers to an argument tuple'
    return tuple(map(int, arg.split()))

if __name__ == '__main__':
    TurtleShell().cmdloop()