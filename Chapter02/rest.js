#!/usr/bin/env node

const https = require("https");
const fs = require("fs");
const os = require("os");

const argparse = require("argparse");
const getpass = require("getpass");

// Make the HTTPS request and set up handlers for subsequent events
var httpsRequest = function(args) {
    var mimeType="text/xml";
    if (args.t=="json") mimeType="application/json";
    if (args.t=="text") mimeType="text/plain";

    var req = https.request({
        hostname: args.target,
        port: args.p,
        path: "/rpc/"+args.r,
        method: "GET",
        auth: args.u+":"+password,
        headers: {
            'Accept': mimeType,
        },
        ca: args.c?[fs.readFileSync(args.c, {encoding: 'utf-8'})]:[],
        rejectUnauthorized: args.c?true:false,
        checkServerIdentity: function (host, cert) { return undefined; }
    }, function(response) {
        console.log(response.statusCode, response.statusMessage);
        // console.log('headers:', response.headers);
        response.on('data', function(data) {
            process.stdout.write(data);
        });
    });

    req.on('error', function(err) {
        console.error(err);
    });

    req.end();
}

// Read the command line
var cmdline = new argparse.ArgumentParser({description: "NodeJS JUNOS REST Client"});
cmdline.addArgument("target", { help: "Target router to query" } )
cmdline.addArgument("-t", { choices: ["xml", "json", "text"], help: "Type of output", defaultValue: "xml" } )
cmdline.addArgument("-r", { metavar: "rpc-call", help: "RPC call to make", defaultValue: "get-software-information" } )
cmdline.addArgument("-c", { metavar: "certificate", help: "Router's self-signed certificate .pem file" } )
cmdline.addArgument("-p", { metavar: "port", help: "TCP port", defaultValue: 8443 } )
cmdline.addArgument("-u", { metavar: "username", help: "Remote username", defaultValue: os.userInfo()['username'] } )

// MAIN
var args = cmdline.parseArgs();

var password=null;

try {
    var passwordFile = os.userInfo()['homedir']+"/.pwaccess";
    var stat = fs.statSync(passwordFile);
    if ((stat.mode & 63) == 0) {
        var passwordList = JSON.parse(fs.readFileSync(passwordFile));
        password = passwordList[args.u+"@"+args.target].toString();
    } else {
        console.warn("Warning: password file " + passwordFile + " must be user RW (0600) only!\n");
        process.exit(1);
    }
    process.nextTick(httpsRequest, args);
}
catch (e) {
    getpass.getPass(function(err, pwd) { 
        if (err) { console.warn(err) }
        else {
            password = pwd;
            process.nextTick(httpsRequest, args);
        }
    });
}




