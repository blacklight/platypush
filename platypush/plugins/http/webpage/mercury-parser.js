#!node

// This script will parse the content and title of a webpage using the
// mercury-parser JavaScript library (https://github.com/postlight/mercury-parser)
// and print a JSON object with the extracted information.

'use strict';

const parser = require('@postlight/mercury-parser');

if (process.argv.length < 3) {
    console.error('Usage: ' + process.argv[1] + ' <url to parse>');
    process.exit(1);
}

const url = process.argv[2];
parser.parse(url).then(result => {
    console.log(JSON.stringify(result));
});

