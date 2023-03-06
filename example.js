const { collector } = require("./build");
const { join } = require("path");

(async () => {
  const EMULATE_DEVICE = "iPhone X";

  // Save the results to a folder
  let OUT_DIR = true;

  // The URL to test
  const URL = "${{ github.event.inputs.url }}";
  const inUrl = URL.startsWith("http") ? URL : `http://${URL}`;

  const defaultConfig = {
    inUrl,
    numPages: 3,
    headless: true,
    emulateDevice: EMULATE_DEVICE,
  };

//   const result = await collector(
//     OUT_DIR
//       ? { ...defaultConfig, ...{ outDir: join(__dirname, URL) } }
//       : defaultConfig
//   );
//   if (OUT_DIR) {
//     console.log(
//       `For captured data please look in ${join(__dirname, URL)}`
//     );
//   }
// })();
  if (OUT_DIR) {
    const artifactName = `${URL}-${process.env.BUILD_ID}.tar.gz`;
    const artifactPath = join(__dirname, URL, `${URL}.tar.gz`);
    console.log(`Saving artifact ${artifactName}`);
    console.log(`Artifact path: ${artifactPath}`);
    await uploadArtifact(artifactName, [artifactPath]);
  }

  if (OUT_DIR) {
    console.log(
      `For captured data please look in ${join(__dirname, URL)}`
    );
  }
})();

async function uploadArtifact(name, files) {
  const artifact = {
    name: name,
    path: files,
  };
  try {
    const artifactClient = artifact.create();
    await artifactClient.uploadArtifact(name, files, __dirname);
  } catch (error) {
    console.log(error);
  }
}
