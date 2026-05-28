#!/usr/bin/node

// This script will parse the content and title of a webpage using the
// Mozilla Readability library (https://github.com/mozilla/readability)

'use strict';

const fs = require('fs');
const { JSDOM } = require('jsdom');
const { Readability } = require('@mozilla/readability');

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
  result.headers['User-Agent'] = result.headers['User-Agent'] || 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36';
  return result;
};

const parse = async (url, args) => {
  if (!args?.html?.length) {
    // Fetch the URL
    const response = await fetch(url, {
      headers: args.headers,
    });

    if (!response.ok) {
      console.error(`Failed to fetch ${url}: ${response.statusText}`);
      process.exit(1);
    }

    args.html = await response.text();
  }

  const doc = new JSDOM(args.html);
  const content = new Readability(doc.window.document).parse();
  console.log(JSON.stringify({
    title: content.title,
    content: content.content,
  }));
};

const main = async () => {
  const args = parseArgs(process.argv);
  const contentFile = args.contentFile;
  const url = args.url;
  delete args.url;

  if (contentFile) {
    delete args.contentFile;

    fs.readFile(contentFile, 'utf8', async (err, data) => {
      if (err) {
        console.error(err);
        process.exit(1);
      }

      args.html = data;
      await parse(url, args);
    });
  } else {
    await parse(url, args);
  }
}

main();
