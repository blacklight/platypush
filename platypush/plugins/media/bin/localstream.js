#!/usr/bin/env node

// Requires:
//      - express (`npm install express`)
//      - mime-types (`npm install mime-types`)

const express = require('express')
const fs = require('fs')
const path = require('path')
const process = require('process')
const mime = require('mime-types')
const app = express()

function parseArgv() {
    let file = undefined
    let port = 8989

    if (process.argv.length < 3) {
        throw Error(`Usage: ${process.argv[0]} ${process.argv[1]} <media_file> [port=${port}]`)
    }

    file = process.argv[2]

    if (process.argv.length > 3) {
        port = parseInt(process.argv[3])
    }

    return { file: file, port: port }
}

let args = parseArgv()

app.get('/video', function(req, res) {
  const path = args.file
  const ext = args.file.split('.').pop()
  const stat = fs.statSync(path)
  const fileSize = stat.size
  const range = req.headers.range
  const mimeType = mime.lookup(ext)

  if (range) {
    const parts = range.replace(/bytes=/, "").split("-")
    const start = parseInt(parts[0], 10)
    const end = parts[1]
      ? parseInt(parts[1], 10)
      : fileSize-1

    const chunksize = (end-start)+1
    const file = fs.createReadStream(path, {start, end})
    const head = {
      'Content-Range': `bytes ${start}-${end}/${fileSize}`,
      'Accept-Ranges': 'bytes',
      'Content-Length': chunksize,
      'Content-Type': mimeType,
    }

    res.writeHead(206, head)
    file.pipe(res)
  } else {
    const head = {
      'Content-Length': fileSize,
      'Content-Type': mimeType,
    }
    res.writeHead(200, head)
    fs.createReadStream(path).pipe(res)
  }
})

app.listen(args.port, function () {
  console.log(`Listening on port ${args.port}`)
})
