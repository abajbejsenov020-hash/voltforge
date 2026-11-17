export class HttpError extends Error {
  constructor(status, code, message, details) {
    super(message);
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

export function sendJson(response, status, value) {
  const body = JSON.stringify(value);
  response.writeHead(status, {
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': Buffer.byteLength(body),
    'Cache-Control': 'no-store',
  });
  response.end(body);
}

export function readJson(request, limit = 1024 * 1024) {
  if (
    (request.headers['content-type'] || '').split(';')[0].trim().toLowerCase() !==
    'application/json'
  ) {
    request.resume();
    throw new HttpError(415, 'UNSUPPORTED_MEDIA_TYPE', 'Send the request as application/json.');
  }
  return new Promise((resolve, reject) => {
    let size = 0;
    let settled = false;
    const chunks = [];
    const fail = (error) => {
      if (!settled) {
        settled = true;
        chunks.length = 0;
        reject(error);
      }
    };
    const tooLarge = () =>
      fail(new HttpError(413, 'BODY_TOO_LARGE', 'The request body exceeds 1 MiB.'));
    if (Number(request.headers['content-length']) > limit) tooLarge();
    request.on('data', (chunk) => {
      if (settled) return;
      size += chunk.length;
      if (size > limit) tooLarge();
      else chunks.push(chunk);
    });
    request.on('end', () => {
      if (settled) return;
      settled = true;
      try {
        const body = JSON.parse(Buffer.concat(chunks).toString('utf8'));
        if (!body || Array.isArray(body) || typeof body !== 'object')
          throw new Error('Expected an object');
        resolve(body);
      } catch {
        reject(new HttpError(400, 'INVALID_JSON', 'The request body must be a JSON object.'));
      }
    });
    request.on('error', () =>
      fail(new HttpError(400, 'INCOMPLETE_REQUEST', 'The request body could not be read.')),
    );
    request.on('aborted', () =>
      fail(new HttpError(400, 'INCOMPLETE_REQUEST', 'The request was interrupted.')),
    );
  });
}
