
#!/usr/bin/python



from scipy.stats import zipf
from random import gauss
import numpy as np
import math
import random as rand




nodes = []


f = open("topo.top","r")
f_traf = open ("traff.traf","r")
f_tcl = open ("1.tcl","w")

f_tcl.write("set ns [new Simulator]\n")
f_tcl.write("proc finish {} { \n")
f_tcl.write("    global ns\n")
f_tcl.write("    $ns flush-trace\n")
f_tcl.write("    exit 0\n")
f_tcl.write("}\n")










Time = 300 






for line in f :
	content = line.rstrip('\n\r').split(" ")

	if content[0] not in nodes:
		nodes.append(content[0])
		f_tcl.write("set n%s [$ns node]\n" %(content[0]))

	if content[1] not in nodes:
		nodes.append(content[1])
		f_tcl.write("set n%s [$ns node]\n" %(content[1]))

	f_tcl.write("$ns duplex-link $n%s $n%s %sKb %sms RED\n" %(content[0], content[1],content[2],content[3]))
	f_tcl.write("$ns queue-limit $n%s $n%s 100\n" %(content[0],content[1]))
	f_tcl.write("$ns duplex-link-op $n%s $n%s queuePos 0.5\n" %(content[0],content[1]))
	
	#setting du monitor queue
	f_tcl.write("set (traceq-%s-%s) [open queues/queue-%s-%s.tr w]\n" %( content[0], content[1],content[0], content[1]))
	f_tcl.write("set (queue-%s-%s) [$ns monitor-queue $n%s $n%s  $(traceq-%s-%s) 0.1]\n" %(content[0], content[1],content[0], content[1],content[0], content[1]))
	f_tcl.write("[$ns link $n%s $n%s] queue-sample-timeout\n" %(content[0], content[1]))








links = []
for line in f_traf :
	content = line.rstrip('\n\r').split(" ")

	#division en deux partie entiere
	traff_send = float(content[2])
	tcp_send = int (math.floor(traff_send*0.2))
	pareto_send = int (math.floor(traff_send*0.8))

	links.append("%s-%s" %(content[0], content[1]))   


	#creation sources tcp
	f_tcl.write("set (tcp_src-%s-%s) [new Agent/TCP/Reno]\n" %(content[0], content[1]))
	f_tcl.write("	$(tcp_src-%s-%s) set window_ 64\n" %(content[0], content[1]))
	

	f_tcl.write("$ns attach-agent $n%s $(tcp_src-%s-%s)\n" %(content[0], content[0], content[1]))
	

	f_tcl.write("set (tcp_snk-%s-%s) [new Agent/TCPSink]\n"	%(content[0], content[1]))
	

	f_tcl.write("$ns attach-agent $n%s $(tcp_snk-%s-%s)\n" %(content[1], content[0],content[1]))
	

	#connection sources destinations
	f_tcl.write("$ns connect $(tcp_src-%s-%s) $(tcp_snk-%s-%s)\n" %(content[0], content[1], content[0],content[1]))

	#fichiers de trace de la cwnd et de la bw
	f_tcl.write("set (g-%s-%s) [open sinks/sink-%s-%s.tr w]\n"%(content[0], content[1],content[0], content[1]))
	f_tcl.write("set (f-%s-%s) [open outs/flux_%s_%s.tr w]\n" %(content[0], content[1],content[0], content[1]))
	
	
	#agent udp
	f_tcl.write("set (udp_src-%s-%s) [new Agent/UDP]\n" %(content[0], content[1]))
	f_tcl.write("$ns attach-agent $n%s $(udp_src-%s-%s)\n" %(content[0], content[0], content[1]))
	f_tcl.write("set (udp_snk-%s-%s) [new Agent/Null]\n"	%(content[0], content[1]))
	f_tcl.write("$ns attach-agent $n%s $(udp_snk-%s-%s)\n" %(content[1], content[0],content[1]))
	f_tcl.write("$ns connect $(udp_src-%s-%s) $(udp_snk-%s-%s)\n" %(content[0], content[1], content[0],content[1]))

	#agents pareto over udp
	f_tcl.write("set (p-%s-%s) [new Application/Traffic/Pareto]\n" %(content[0], content[1]))
	f_tcl.write("$(p-%s-%s) set burst_time_ 500ms" %(content[0], content[1]))
	f_tcl.write("$(p-%s-%s) set idle_time_ 500ms" %(content[0], content[1]))
	f_tcl.write("$(p-%s-%s) set rate_ 200k" %(content[0], content[1]))
	f_tcl.write("$(p-%s-%s) set shape 1.5" %(content[0], content[1]))
	f_tcl.write("$(p-%s-%s) attach-agent $(udp_src-%s-%s)\n" %(content[0], content[1], content[0], content[1]))	




	S = 0
	while S < tcp_send  :
		#changmt des loi a "volente"
		random_start = np.random.normal(150,75)
		random_traf = rand.uniform(0,.001)*tcp_send
		if random_traf < tcp_send :
			#envoi de la partition "amplifiee" pour creer des congestions
			f_tcl.write("$ns at %s \"$(tcp_src-%s-%s) send %s\"\n" %(random_start,content[0], content[1],(random_traf*10000000000)))
			S = S + random_traf

	
		


#fonction record enregistrement de la bandwidth et de la cwnd
f_tcl.write("proc record {tcp_src tcp_snk file_src file_snk} { \n")
f_tcl.write("\tset ns_inst [Simulator instance] \n")
f_tcl.write("\tset time 1\n")
f_tcl.write("\tset cwnd [$tcp_src set cwnd_]\n")
f_tcl.write("\tset bw [$tcp_snk set bytes_]\n")
f_tcl.write("\tset now [$ns_inst now]\n")
f_tcl.write("\tputs $file_src \"$now [expr $cwnd ]\"\n")
f_tcl.write("\tputs $file_snk \"$now [expr $bw ]\"\n")
f_tcl.write("\t$ns_inst at [expr $now+$time] \"record $tcp_src $tcp_snk $file_src $file_snk\"\n")
f_tcl.write("}\n")


#appel de la fction record 
for l in links :
	f_tcl.write("$ns at 0 \"record $(tcp_src-%s) $(tcp_snk-%s) $(f-%s) $(g-%s)\"\n" %(l, l, l, l))


	






f_tcl.write("$ns at 300 \"finish\"\n ")
f_tcl.write("$ns run")

f.close()
f_tcl.close()

