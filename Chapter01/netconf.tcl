#!/usr/bin/env expect


# Utility function to call an RPC and capture the response
proc cmdrpc { cmd } {
    send -- "<rpc><command format=\"text\">[join $cmd]</command></rpc>\r\n"
    set output ""
    expect {

        # Catch any RPC errors, outputting context
        -re {<error-message>([^<]+)</error-message>} {
            send_error "Command RPC for $cmd caused error: $expect_out(1,string)\r\n"
            return
    }

        # Real output
        -re {<(configuration-)?output[^>]*>} {
            expect {
                -re {^[^<]+} {
                    append output $expect_out(0,string)
                    exp_continue
                }
                -re "</(configuration-)?output>" {}
            }
            regsub -all "&lt;" $output "<" output
            regsub -all "&gt;" $output ">" output
            regsub -all "&amp;" $output "&" output
            return $output
        }

        default {
            send_error "Timeout waiting for RPC [join $cmd]\r\n"
			send_error [ 
				concat "\t" [ regsub -all {[\r\n]+} $expect_out(buffer) "\r\n\t" ]
			]
            return
        }
    }
}


# Parse the command line arguments
log_user 0

if { [ llength $argv ] != 2 } {
	send_user "Usage: netconf.tcl hostname command\r\n"
	exit 1
}
set hostname [lrange $argv 0 0]
set command [lrange $argv 1 1]

# Establish SSH and call procedure
set DELIMITER {]]>]]>}

if [ spawn -noecho ssh -q -p 830 -i junos_auto_id_rsa auto@$hostname -s netconf ] {
	expect {
		$DELIMITER {
			set result [ cmdrpc $command ]
			if {$result ne ""} {
				send_user $result
			}
		}
		default {
			send_error "SSH protocol error (check authorized_keys?)\r\n"
            exit 1
		}
	}
} {
	send_error "Unable to start SSH client for connection to $hostname\r\n"
    exit 1
}
close
exit

