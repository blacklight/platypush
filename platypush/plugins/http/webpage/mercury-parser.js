#!/usr/bin/node

// This script will parse the content and title of a webpage using the
// mercury-parser JavaScript library (https://github.com/postlight/mercury-parser)
// and print a JSON object with the extracted information.

'use strict';

const fs = require('fs');
const Mercury = require('@postlight/mercury-parser');

const usage = () => {
  console.error(
    'Usage: ' + process.argv[1] + ' <url to parse> [--user-agent "some-user-agent"] ' +
    '[--cookie "some-cookie"] [--some-header "some-value"] [markdown|html|text] [Pre-fetched HTML content file]'
  );

  process.exit(1);
};

const parseArgs = (args) => {
  const result = {
    headers: {},
  };

  let pos = 0;

  for (let i = 1; i < args.length; i++) {
    const arg = args[i];
    if (arg.startsWith('--') && i < args.length - 1 && !args[i + 1].startsWith('--')) {
      const key = arg.substring(2).toLowerCase();
      const value = args[++i];
      result.headers[key] = value;
    } else if (pos == 0 && arg.match(/^https?:\/\//)) {
      result.url = arg;
      pos++;
    } else if (pos == 1) {
      result.contentType = arg;
      pos++;
    } else if (pos == 2) {
      result.contentFile = arg;
      pos++;
    }
  }

  if (!result.url?.length) {
    usage();
  }

  result.contentType = result.contentType || 'html';
  result.headers['User-Agent'] = result.headers['User-Agent'] || 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1';
  return result;
};

const parse = (url, args) => {
  Mercury.parse(url, args).then(result => {
    console.log(JSON.stringify(result));
  });
};

const args = parseArgs(process.argv);
const contentFile = args.contentFile;
const url = args.url;
delete args.url;

if (contentFile) {
  delete args.contentFile;

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
