const FORMAT = 'voltmodd-builds';
const VERSION = 1;
const MAX_BYTES = 8 * 1024 * 1024;
const isRecord = (value) => value && typeof value === 'object' && !Array.isArray(value);

export class BuildFileError extends Error {}

function checkSize(blob) {
  if (blob.size > MAX_BYTES) throw new BuildFileError('Build files must be 8 MB or smaller.');
}

export function createBuildFile(builds) {
  const portable = builds.map(({ revision, ...build }) => build);
  const file = new Blob([JSON.stringify({ format: FORMAT, version: VERSION, builds: portable })], {
    type: 'application/json',
  });
  checkSize(file);
  return file;
}

export async function readBuildFile(file) {
  checkSize(file);
  let data;
  try {
    data = JSON.parse(await file.text());
  } catch {
    throw new BuildFileError('This file is not readable JSON. Choose a VOLTMODD build file.');
  }
  if (!isRecord(data) || data.format !== FORMAT || data.version !== VERSION)
    throw new BuildFileError('Choose a build file downloaded from the VOLTMODD garage.');
  if (
    !Array.isArray(data.builds) ||
    !data.builds.length ||
    !data.builds.every(
      (build) =>
        isRecord(build) &&
        typeof build.id === 'string' &&
        typeof build.name === 'string' &&
        ['bike', 'scooter'].includes(build.type) &&
        ['new', 'rebuild'].includes(build.mode) &&
        isRecord(build.selected),
    )
  ) {
    throw new BuildFileError('This file does not contain a valid garage of builds.');
  }
  return data.builds;
}
