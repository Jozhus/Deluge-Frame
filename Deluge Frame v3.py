import subprocess, re, os, time

class torrent:
    """
    info = dict()
    keys = ["Name", "ID", "State", "Down Speed", "Up Speed", "Seeds", "Peers", "Availability", "Size", "Ratio", "Seed time", "Active", "Tracker status", "Progress", '']
    """
    name, ID, state, down, up, eta, seeds, peers, availability, size, ratio, seedtime, activetime, tracker, progress = '', '' ,'' ,'' ,'' ,'' ,'', '', '', '', '', '', '', '', ''
    bar = "[~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~]"
    
    def __init__(self, data):
        self.update(data)
        
    def update(self, data):
        """ I'm sacrificing neatness for ease of use :(
        for i in range(len(self.keys) - 1):
            self.info[self.keys[i]] = re.search(self.keys[i] + ": (.*) " + self.keys[i + 1], data).group(1)
        """
        self.name = re.search("Name: (.*) ID", data).group(1).replace(u'\u012B', 'i')
        self.ID = re.search("ID: (.*) State", data).group(1)
        try:
            self.progress = re.search("Progress: (.*%) ", data).group(1)
            self.bar = re.search("% (\[.*\])", data).group(1).replace('~', '_')
            self.seeds = re.search("Seeds: (.*) Peers", data).group(1)
            self.peers = re.search("Peers: (.*) Availability", data).group(1)
            self.size = re.search("Size: (.*) Ratio", data).group(1)
            self.activetime = re.search("Active: (.*) Tracker status", data).group(1)
            self.state = re.search("State: (.*) Down Speed", data).group(1)
            self.down = re.search("Down Speed: (.*) Up Speed", data).group(1)
            self.availability = re.search("Availability: (.*) Size", data).group(1)
            self.ratio = re.search("Ratio: (.*) Seed time", data).group(1)
            self.seedtime = re.search("Seed time: (.*) Active", data).group(1)
            self.tracker = re.search("Tracker status: (.*) Progress", data).group(1)
        except AttributeError:
            try:
                self.down = "0.0 KiB/s"
                self.state = re.search("State: (.*) Up Speed", data).group(1)
            except AttributeError:
                try:
                    self.up = "0.0 KiB/s"
                    self.state = re.search("State: (.*) Seeds", data).group(1)
                except AttributeError:
                    self.state = "Error"
                    self.eta = "Never"
            return
        try:
            self.up = re.search("Up Speed: (.*) ETA", data).group(1)
            self.eta = re.search("ETA: (.*) Seeds", data).group(1)
        except AttributeError:
            self.up = re.search("Up Speed: (.*) Seeds", data).group(1)
            self.eta = "Never"
        
torrents = []

def update():
    global torrents
    read = [x.replace('\r\n', ' ') for x in subprocess.Popen(["G:/Program Files (x86)/Deluge/deluge-console.exe", "info"], stdout=subprocess.PIPE).communicate()[0].decode('utf-8').split('\r\n \r\n')]
    if read[0] == '':
        return
    for data in read:
        if not torrents:
            torrents.append(torrent(data))
            continue
        check = torrent(data).ID
        for x in torrents:
            if x.ID == check:
                x.update(data)
                break
        if not any(check == x.ID for x in torrents):
            torrents.append(torrent(data))

def display():
    switch = (time.localtime()[5] // 3) % 2
    if switch:
        for item in torrents:
            """
            print(item.bar)
            print("Name:     " + item.name)
            print("ID:       " + item.ID)
            print("State:    " + item.state)
            print("Seeds:    " + item.seeds)
            print("Peers:    " + item.peers)
            print("Size:     " + item.size)
            print("Down:     " + item.down)
            print("Up:       " + item.up)
            print("ETA:      " + item.eta)
            print("Progress: " + item.progress)
            print("Time:     " + item.activetime)
            """
            print(item.bar + ' ' + item.progress)
            print(item.name[:79])
            print(item.state)
            print(item.size)
            print('D: ' + item.down + '/U: ' + item.up)
            print(item.eta)
            print()
    else:
        for item in torrents:
            print(item.bar + ' ' + item.progress)
            print(item.name[:79])
            print(item.state)
            print(item.size)
            print('S: ' + item.seeds + '/P: ' + item.peers)
            print(item.activetime)
            print()

def autoHandle():
    dfolder = 'Downloads' #Files in this folder with the '.torrent' extension will automatically be added.
    cidpath = 'data'
    deluge = 'G:/Program Files (x86)/Deluge/deluge-console.exe' #Deluge console path
    toadd = [x for x in os.listdir(dfolder) if ".torrent" in x]
    if not os.path.isfile(cidpath + '/torrentids.txt'):
            file = open(cidpath + '/torrentids.txt', 'w')
            file.close()
    if not os.path.isfile(cidpath + '/delete torrents.txt'):
            file = open(cidpath + '/delete torrents.txt', 'w')
            file.close()
    for i, file in enumerate(toadd):
        os.rename(dfolder + '/' + file, dfolder + '/' + str(i) + '.torrent')
        subprocess.run([deluge, 'add ' + dfolder + '/' + str(i) + '.torrent'])
        os.remove(dfolder + '/' + str(i) + '.torrent')
    file = open(cidpath + '/torrentids.txt', 'w')
    for item in torrents:
        if item.state == "Error":
            subprocess.run([deluge, 'resume ' + item.ID])
        elif item.state == "Seeding":
            subprocess.run([deluge, 'rm ' + item.ID])
            torrents.remove(item)
        file.write(item.ID + ' - ' + item.name + '\n')
    file.close()
    file = open(cidpath + '/delete torrents.txt', 'r')
    toremove = file.read().split('\n')
    file.close()
    file = open(cidpath + '/delete torrents.txt', 'w')
    file.close()
    if not toremove[0] == '':
        for torrentID in toremove:
            subprocess.run([deluge, 'rm ' + torrentID])
            for item in torrents:
                if item.ID == torrentID:
                    torrents.remove(item)

def loop():
    while(1):
        update()
        autoHandle()
        os.system('cls')
        display()

if 'deluged.exe' not in [x.split(' ')[0] for x in subprocess.Popen(["tasklist"], stdout=subprocess.PIPE).communicate()[0].decode('utf-8').split("\r\n")]:
    os.startfile("G:/Program Files (x86)/Deluge/deluged.exe")
    time.sleep(10)
loop()
