#!/usr/bin/env node

const util = require("util");
const child_process = require('child_process');
const xml2js = require('xml2js');

const DELIMITER="]]>]]>";

const xmlRpcCommand = function(command) {
        return [
                "<rpc>\n",
                "<command format=\"text\">\n",
                command,
                "</command>",
                "</rpc>\n",
                DELIMITER,
                "\n"
        ];
};

var walk = function(obj, path) {
	var result = obj;
	path.forEach(function (cur, ind, array) {
		if (result) result=result[cur];
	});
	return result;
}


if (process.argv.length!=4) {
	console.warn("Usage: netconf.js user@hostname command\n");
	process.exit(1);
}
var hostname = process.argv[2];
var command = process.argv[3];

var child = child_process.spawn(
	"/usr/bin/ssh", [
        "auto@"+hostname,
        "-q",
		"-p", "830",
		"-i", "junos_auto_id_rsa",
		"-s", "netconf"
	]
);

var data="";


child.stderr.on('data', function(chunk) { process.stderr.write(chunk, "utf8"); });
child.stdout.on('data', function(chunk) {
	data+=chunk;
	if ((index=data.indexOf(DELIMITER))!=-1) {
		var xml = data.slice(0, index);
		data = data.slice(index + DELIMITER.length);
		xml2js.parseString(xml, function(err, result) {
			if (err) throw err;
			if (result['hello']) return;
			if (output=walk(result, ['rpc-reply', 'output', 0])) {
				console.log(output);
			} else if (config=walk(result, ['rpc-reply', 'configuration-information', 0, 'configuration-output', 0])) {
				console.log(config);
			} else if (error=walk(result, ['rpc-reply', 'rpc-error', 0, 'error-message', 0])) {
				console.log(error);
			} else {
				console.log("Unexpected empty response");
			}
			child.stdin.end();
		});
	}
});

child.on('error', function(err) { console.log("SSH client error: ", err); })

xmlRpcCommand(command).forEach(function(cur, ind, array) { child.stdin.write(cur, "utf8")} );

