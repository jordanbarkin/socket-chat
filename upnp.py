import miniupnpc

def init_upnp(PORT):
    u = miniupnpc.UPnP()
    u.discoverdelay = 200
    u.discover()
    print('Discovering... delay=%ums' % u.discoverdelay)
    ndevices = u.discover()
    print(ndevices, 'device(s) detected')
    # select an igd
    u.selectigd()
    # display information about the IGD and the internet connection
    print('local ip address :', u.lanaddr)
    externalipaddress = u.externalipaddress()
    print('external ip address :', externalipaddress)
    print(u.statusinfo(), u.connectiontype())

    # addportmapping(external-port, protocol, internal-host, internal-port, description, remote-host)
    # find a free port for the redirection
    r = u.getspecificportmapping(PORT, 'TCP')
    while r != None and PORT < 65536:
        PORT = PORT + 1
        r = u.getspecificportmapping(PORT, 'TCP')

    print('trying to redirect %s port %u TCP => %s port %u TCP' % (externalipaddress, PORT, u.lanaddr, PORT))

    b = u.addportmapping(PORT, 'TCP', u.lanaddr, PORT,
                        'UPnP IGD Tester port %u' % PORT, '')

    return PORT
