const http = require('http');
const https = require('https');
const url = require('url');

const server = http.createServer((req, res) => {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  // Extract target URL from query parameter
  const parsedUrl = url.parse(req.url, true);
  const targetUrl = parsedUrl.query.url;

  if (!targetUrl) {
    res.writeHead(400);
    res.end('Missing url parameter');
    return;
  }

  // Forward request
  const options = {
    method: req.method,
    headers: req.headers
  };

  const proxyReq = https.request(targetUrl, options, (proxyRes) => {
    res.writeHead(proxyRes.statusCode, proxyRes.headers);
    proxyRes.pipe(res);
  });

  req.pipe(proxyReq);
});

server.listen(8080, () => {
  console.log('CORS proxy running on http://localhost:8080');
  console.log('Usage: http://localhost:8080?url=https://api.example.com/endpoint');
});