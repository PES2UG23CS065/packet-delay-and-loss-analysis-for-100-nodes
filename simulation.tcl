# Create simulator
set ns [new Simulator]

# Output files
set tracefile [open out.tr w]
$ns trace-all $tracefile
set namfile [open out.nam w]
$ns namtrace-all $namfile

# Finish procedure
proc finish {} {
    global ns tracefile namfile
    $ns flush-trace
    close $tracefile
    close $namfile
    exec nam out.nam &
    exit 0
}

# Create 100 wireless nodes
for {set i 0} {$i < 100} {incr i} {
    set n($i) [$ns node]
}

# Grid layout
for {set i 0} {$i < 100} {incr i} {
    set x [expr ($i % 10) * 70]
    set y [expr int($i / 10) * 70]
    $n($i) set X_ $x
    $n($i) set Y_ $y
    $n($i) set Z_ 0
}

# Connect node 0 to all others with queue limits
for {set i 1} {$i < 100} {incr i} {
    $ns duplex-link $n(0) $n($i) 1Mb 10ms DropTail
    $ns queue-limit $n(0) $n($i) 10
}

# Setup random traffic (TCP, UDP, CBR)
for {set i 1} {$i < 100} {incr i} {
    set traffic_type [expr int(rand() * 3)]

    if {$traffic_type == 0} {
        set tcp($i) [new Agent/TCP]
        $ns attach-agent $n(0) $tcp($i)

        set sink($i) [new Agent/TCPSink]
        $ns attach-agent $n($i) $sink($i)
        $ns connect $tcp($i) $sink($i)

        set ftp($i) [new Application/FTP]
        $ftp($i) attach-agent $tcp($i)

        set start_time [expr rand()*5]
        set stop_time [expr $start_time + 1]
        $ns at $start_time "$ftp($i) start"
        $ns at $stop_time "$ftp($i) stop"
    } else {
        set udp($i) [new Agent/UDP]
        $ns attach-agent $n(0) $udp($i)

        set nullsink($i) [new Agent/Null]
        $ns attach-agent $n($i) $nullsink($i)
        $ns connect $udp($i) $nullsink($i)

        if {$traffic_type == 2} {
            set cbr($i) [new Application/Traffic/CBR]
            $cbr($i) set packetSize_ 1000
            $cbr($i) set interval_ 0.01
            $cbr($i) attach-agent $udp($i)

            set start_time [expr rand()*5]
            set stop_time [expr $start_time + 1]
            $ns at $start_time "$cbr($i) start"
            $ns at $stop_time "$cbr($i) stop"
        }
    }
}

$ns at 6.0 "finish"
$ns run
