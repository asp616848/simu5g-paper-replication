package validation.networks;

import inet.networklayer.configurator.ipv4.Ipv4NetworkConfigurator;
import inet.node.ethernet.Eth10G;
import inet.node.inet.Router;
import inet.node.inet.StandardHost;
import simu5g.common.binder.Binder;
import simu5g.common.carrierAggregation.CarrierAggregation;
import simu5g.corenetwork.bearerConfigurator.BearerConfigurator;
import simu5g.nodes.ExtCell;
import simu5g.nodes.NrUe;
import simu5g.nodes.Upf;
import simu5g.nodes.gNodeB;
import simu5g.world.radio.LteChannelControl;

//
// 3GPP Urban Macro validation scenario of Simu5G paper (Sec. IV-E, Fig. 14).
//
// The central site hosts three full-stack gNBs (the cells under study); the
// remaining 18 sites (54 cells) are "light cells" (ExtCell) that transmit on
// the whole spectrum and only produce inter-cell interference.
// Positions, sector azimuths and UE drops are set from generated .ini files.
//
network UrbanMacro
{
    parameters:
        int numUe = default(30);
        int numExtCells = default(54);
        **.cellularNic.hasSdap = default(true);
        @display("bgb=2200,2200");
    submodules:
        channelControl: LteChannelControl;
        configurator: Ipv4NetworkConfigurator;
        binder: Binder;
        bearerConfigurator: BearerConfigurator;
        carrierAggregation: CarrierAggregation;
        server: StandardHost;
        router: Router;
        upf: Upf;
        iUpf: Upf;
        gnb[3]: gNodeB;
        extCell[numExtCells]: ExtCell;
        ue[numUe]: NrUe;
    connections:
        server.pppg++ <--> Eth10G <--> router.pppg++;
        router.pppg++ <--> Eth10G <--> upf.dnPppg;
        upf.pppg++ <--> Eth10G <--> iUpf.pppg++;
        for i=0..2 {
            iUpf.pppg++ <--> Eth10G <--> gnb[i].ppp;
        }
}
