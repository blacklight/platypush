#!node

// This script will parse the content and title of a webpage using the
// mercury-parser JavaScript library (https://github.com/postlight/mercury-parser)
// and print a JSON object with the extracted information.

'use strict';

const parser = require('@postlight/mercury-parser');

if (process.argv.length < 3) {
    console.error('Usage: ' + process.argv[1] + ' <url to parse> [markdown|html] [Pre-fetched content]');
    process.exit(1);
}

const url = process.argv[2];
const type = process.argv[3] || 'html';
const content = process.argv[4];
const args = {
    contentType: type,
    html: content,
};

parser.parse(url, args).then(result => {
    console.log(JSON.stringify(result));
});

