const { collector } = require("./build");
const { join } = require("path");

(async () => {
  const EMULATE_DEVICE = "iPhone X";

  // Save the results to a folder
  let OUT_DIR = true;

  // The URL to test
  const URL = process.argv[2];
  const inUrl = URL.startsWith("http") ? URL : `https://${URL}`;
  if (inUrl.endsWith("/")) {
  inUrl = inUrl.slice(0, -1);
  }
  if (inUrl.endsWith("/search")) {
  // Remove "/search" from the link
  inUrl = inUrl.slice(0, -"/search".length);
  }
  
  let cleanUrl = URL.replace("https://", "").replace("http://", "");
  var index = cleanUrl.indexOf("/");
  if (index !== -1) {
  cleanUrl = cleanUrl.substring(0, index);
  }

  const defaultConfig = {
    inUrl,
    numPages: 3,
    headless: true,
    emulateDevice: EMULATE_DEVICE,
  };
  
  console.log(`For fake captured data please look in ${join(__dirname, cleanUrl)}`)
  const result = await collector(
    OUT_DIR
      ? { ...defaultConfig, ...{ outDir: cleanUrl} }
      : defaultConfig
  );
  if (OUT_DIR) {
    console.log(
      `For captured data please look in ${cleanUrl}`
    );
  }
})();
