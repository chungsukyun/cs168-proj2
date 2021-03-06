"""Your awesome Distance Vector router for CS 168."""

import sim.api as api
import sim.basics as basics

# We define infinity as a distance of 16.
INFINITY = 16


class DVRouter(basics.DVRouterBase):
    # NO_LOG = True # Set to True on an instance to disable its logging
    # POISON_MODE = True # Can override POISON_MODE here
    # DEFAULT_TIMER_INTERVAL = 5 # Can override this yourself for testing


    def __init__(self):
        """
        Called when the instance is initialized.

        You probably want to do some additional initialization here.

        """
        self.routingTable = {} # maps ports to latency and hosts
        self.distanceVector = {} # maps hosts to latency and first hop
        self.neighbors = {} # maps ports to latency
        self.directHosts = {}
        self.start_timer()  # Starts calling handle_timer() at correct rate

    def handle_link_up(self, port, latency):
        """
        Called by the framework when a link attached to this Entity goes up.

        The port attached to the link and the link latency are passed
        in.

        """
        self.neighbors[port] = latency
        for host in self.distanceVector.keys():
            packet = basics.RoutePacket(host, self.distanceVector[host][0])
            self.send(packet, port)


    def handle_link_down(self, port):
        """
        Called by the framework when a link attached to this Entity does down.

        The port number used by the link is passed in.

        """
        self.neighbors.pop(port)
        for host in self.distanceVector.keys():
            if self.distanceVector[host][1] == port:
                self.distanceVector.pop(host)
                if host in self.directHosts.keys():
                    self.distanceVector[host] = [self.neighbors[host], self.directHosts[host]]

    def handle_rx(self, packet, port):
        """
        Called by the framework when this Entity receives a packet.

        packet is a Packet (or subclass).
        port is the port number it arrived on.

        You definitely want to fill this in.

        """
        #self.log("RX %s on %s (%s)", packet, port, api.current_time())
        if isinstance(packet, basics.RoutePacket):
            self.routingTable[port] = [packet.latency, packet.destination]
            if packet.destination in self.distanceVector:
                if self.distanceVector[packet.destination][0] >= packet.latency + self.neighbors[port]:
                    self.distanceVector[packet.destination] = [packet.latency + self.neighbors[port], port]
            else:
                self.distanceVector[packet.destination] = [packet.latency + self.neighbors[port], port]
            api.create_timer(15, self.expire_route, False, False, [packet.destination])
        elif isinstance(packet, basics.HostDiscoveryPacket):
            self.distanceVector[packet.src] = [self.neighbors[port], port]
            self.directHosts[packet.src] = port
        else:
            # Totally wrong behavior for the sake of demonstration only: send
            # the packet back to where it came from!
            # self.send(packet, port=port)
            if packet.dst in self.distanceVector:
                if self.distanceVector[packet.dst][1] != port:
                    self.send(packet, self.distanceVector[packet.dst][1])


    def handle_timer(self):
        """
        Called periodically.

        When called, your router should send tables to neighbors.  It
        also might not be a bad place to check for whether any entries
        have expired.

        """
        for port in self.neighbors.keys():
            for host in self.distanceVector.keys():
                if self.distanceVector[host][1] != port:
                    packet = basics.RoutePacket(host, self.distanceVector[host][0])
                    self.send(packet, port)

    def expire_route(self, host):
        if host in self.distanceVector.keys():
            self.distanceVector.pop(host)


