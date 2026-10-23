package validation.networks;

import inet.networklayer.configurator.ipv4.Ipv4NetworkConfigurator;
import inet.node.ethernet.Eth10G;
import inet.node.inet.Router;
import inet.node.inet.StandardHost;
import simu5g.common.binder.Binder;
import simu5g.common.carrierAggregation.CarrierAggregation;
import simu5g.corenetwork.bearerConfigurator.BearerConfigurator;
import simu5g.nodes.NrUe;
import simu5g.nodes.Upf;
import simu5g.nodes.gNodeB;
import simu5g.world.radio.LteChannelControl;

//
// Variant of ~UrbanMacro in which all 57 cells are full-stack gNBs (no light cells).
// UEs 0..29 are the measured UEs of the central site; every other UE is a saturating
// "load" UE that keeps one of the 54 remaining cells at 100% load. Used to test whether
// serving-cell selection among all cells (as in the 3GPP calibration) explains the
// residual SINR gap of the light-cell setup.
//
network UrbanMacroFull
{
    parameters:
        int numUe = default(84);
        int numGnb = default(57);
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
        gnb[numGnb]: gNodeB;
        ue[numUe]: NrUe;
    connections:
        server.pppg++ <--> Eth10G <--> router.pppg++;
        router.pppg++ <--> Eth10G <--> upf.dnPppg;
        upf.pppg++ <--> Eth10G <--> iUpf.pppg++;
        for i=0..numGnb-1 {
            iUpf.pppg++ <--> Eth10G <--> gnb[i].ppp;
        }
}
