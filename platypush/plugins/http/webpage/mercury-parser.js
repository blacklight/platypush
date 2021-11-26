#!node

// This script will parse the content and title of a webpage using the
// mercury-parser JavaScript library (https://github.com/postlight/mercury-parser)
// and print a JSON object with the extracted information.

'use strict';

const fs = require('fs');
const Mercury = require('@postlight/mercury-parser');

if (process.argv.length < 3) {
    console.error('Usage: ' + process.argv[1] + ' <url to parse> [markdown|html|text] [Pre-fetched HTML content file]');
    process.exit(1);
}

const url = process.argv[2];
const type = process.argv[3] || 'html';
const contentFile = process.argv[4];
const args = {
    contentType: type,
};

const parse = (url, args) => {
    Mercury.parse(url, args).then(result => {
        console.log(JSON.stringify(result));
    });
};

if (contentFile) {
    fs.readFile(contentFile, 'utf8', (err, data) => {
        if (err) {
            console.error(err);
            process.exit(1);
        }

        args.html = data;
        parse(url, args);
    });
} else {
    parse(url, args);
}

