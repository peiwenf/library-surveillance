const { collector } = require("./build");
const { join } = require("path");

(async () => {
  const EMULATE_DEVICE = "iPhone X";

  // Save the results to a folder
  let OUT_DIR = true;

  // The URL to test
  const URL = process.argv[2];
  const inUrl = URL.startsWith("http") ? URL : `http://${URL}`;

  const defaultConfig = {
    inUrl,
    numPages: 3,
    headless: true,
    emulateDevice: EMULATE_DEVICE,
  };

  const result = await collector(
    OUT_DIR
      ? { ...defaultConfig, ...{ outDir: join(__dirname, URL) } }
      : defaultConfig
  );
  if (OUT_DIR) {
    console.log(
      `For captured data please look in ${join(__dirname, URL)}`
    );
  }
})();
