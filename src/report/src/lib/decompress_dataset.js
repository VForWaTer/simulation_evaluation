import pako from 'pako';
/**
 * Decompress dataset helper function.
 * 
 * This function handles the decompression of the base64-encoded, gzip-compressed
 * dataset that was embedded in the HTML.
 * 
 * Implementation:
 * 1. Decode base64 string to binary data using atob()
 * 2. Convert binary string to Uint8Array for pako
 * 3. Decompress using pako.inflate() with { to: 'string' } option
 * 4. Parse the resulting JSON string to JavaScript object
 * 
 * @param {string} compressedData - Base64-encoded, gzip-compressed dataset string
 * @returns {Object} Decompressed dataset object
 * 
 * @example
 * const datasets = decompressDataset(datasetCompressed);
 * // Returns: { "DE110000": { index: [...], observation: [...], simulation: [...] }, ... }
 */
export function decompressDataset(compressedData) {
  if (!compressedData) {
    throw new Error('Compressed dataset data is missing');
  }

  // decode the base64 into a binary string
  const binaryString = atob(compressedData);
  const bytes = new Uint8Array(binaryString.length);

  for (let i = 0; i < binaryString.length; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }

  const decompressed = pako.inflate(bytes, {to: 'string'});
  const payload = JSON.parse(decompressed);
  console.log(payload);
  return payload;
}


